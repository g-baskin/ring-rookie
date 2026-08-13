"""Atomic durable claims for idempotent effects."""

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.effect_claim import EffectClaim, EffectClaimStatus

GLOBAL_SCOPE = "global"


class ClaimDisposition(str, Enum):
    ACQUIRED = "acquired"
    COMPLETED = "completed"
    PROCESSING = "processing"


@dataclass(frozen=True)
class ClaimResult:
    disposition: ClaimDisposition
    claim: EffectClaim


def effect_digest(value: bytes | str) -> str:
    """Return only a fixed-length digest; callers must never persist source material."""
    if isinstance(value, str):
        value = value.encode()
    return hashlib.sha256(value).hexdigest()


async def acquire_claim(
    db: AsyncSession, *, scope_key: str, namespace: str, digest: str
) -> ClaimResult:
    """Atomically claim an effect; failed claims may be retried."""
    now = datetime.now(UTC)
    values = {
        "scope_key": scope_key,
        "namespace": namespace,
        "digest": digest,
        "status": EffectClaimStatus.PROCESSING.value,
        "attempt_count": 1,
        "first_attempt_at": now,
        "last_attempt_at": now,
    }
    inserted = False
    if db.bind and db.bind.dialect.name == "postgresql":
        statement = (
            pg_insert(EffectClaim)
            .values(**values)
            .on_conflict_do_nothing(constraint="uq_effect_claim_identity")
            .returning(EffectClaim.id)
        )
        inserted = (await db.execute(statement)).scalar_one_or_none() is not None
        await db.commit()
    else:
        try:
            async with db.begin_nested():
                db.add(EffectClaim(**values))
                await db.flush()
            await db.commit()
            inserted = True
        except IntegrityError:
            await db.rollback()

    query = select(EffectClaim).where(
        EffectClaim.scope_key == scope_key,
        EffectClaim.namespace == namespace,
        EffectClaim.digest == digest,
    )
    claim = (await db.execute(query)).scalar_one()
    if inserted:
        return ClaimResult(ClaimDisposition.ACQUIRED, claim)
    if claim.status == EffectClaimStatus.COMPLETED.value:
        return ClaimResult(ClaimDisposition.COMPLETED, claim)
    if claim.status == EffectClaimStatus.FAILED.value:
        claim.status = EffectClaimStatus.PROCESSING.value
        claim.attempt_count += 1
        claim.last_attempt_at = now
        await db.commit()
        return ClaimResult(ClaimDisposition.ACQUIRED, claim)
    return ClaimResult(ClaimDisposition.PROCESSING, claim)


async def complete_claim(
    db: AsyncSession, claim: EffectClaim, *, response: str, provider_ref: str | None = None
) -> None:
    claim.status = EffectClaimStatus.COMPLETED.value
    claim.response = response
    claim.provider_ref = provider_ref
    claim.completed_at = datetime.now(UTC)
    await db.commit()


async def fail_claim(db: AsyncSession, claim: EffectClaim) -> None:
    claim.status = EffectClaimStatus.FAILED.value
    claim.last_attempt_at = datetime.now(UTC)
    await db.commit()
