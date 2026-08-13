"""Focused tests for durable effect claims."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.models.effect_claim import EffectClaimStatus
from app.services.effect_claims import (
    ClaimDisposition,
    acquire_claim,
    complete_claim,
    effect_digest,
    fail_claim,
)


@pytest.fixture
async def claim_db() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_completed_duplicate_replays_without_raw_key(claim_db: AsyncSession) -> None:
    raw_key = "customer@example.com:+15551234567"
    digest = effect_digest(raw_key)
    first = await acquire_claim(
        claim_db, scope_key="workspace-a", namespace="test.effect", digest=digest
    )
    assert first.disposition == ClaimDisposition.ACQUIRED
    await complete_claim(claim_db, first.claim, response='{"ok":true}', provider_ref="ref-1")

    duplicate = await acquire_claim(
        claim_db, scope_key="workspace-a", namespace="test.effect", digest=digest
    )
    assert duplicate.disposition == ClaimDisposition.COMPLETED
    assert duplicate.claim.response == '{"ok":true}'
    assert duplicate.claim.digest == digest
    assert raw_key not in repr(duplicate.claim.__dict__)


@pytest.mark.asyncio
async def test_processing_double_claim_and_scope_isolation(claim_db: AsyncSession) -> None:
    digest = effect_digest("same-provider-event")
    first = await acquire_claim(
        claim_db, scope_key="workspace-a", namespace="test.effect", digest=digest
    )
    duplicate = await acquire_claim(
        claim_db, scope_key="workspace-a", namespace="test.effect", digest=digest
    )
    isolated = await acquire_claim(
        claim_db, scope_key="workspace-b", namespace="test.effect", digest=digest
    )
    assert first.disposition == ClaimDisposition.ACQUIRED
    assert duplicate.disposition == ClaimDisposition.PROCESSING
    assert isolated.disposition == ClaimDisposition.ACQUIRED
    assert first.claim.id != isolated.claim.id


@pytest.mark.asyncio
async def test_failed_handler_can_be_reacquired(claim_db: AsyncSession) -> None:
    first = await acquire_claim(
        claim_db,
        scope_key=str(uuid.uuid4()),
        namespace="test.retry",
        digest=effect_digest("event"),
    )
    await fail_claim(claim_db, first.claim)
    assert first.claim.status == EffectClaimStatus.FAILED.value

    retry = await acquire_claim(
        claim_db,
        scope_key=first.claim.scope_key,
        namespace=first.claim.namespace,
        digest=first.claim.digest,
    )
    assert retry.disposition == ClaimDisposition.ACQUIRED
    assert retry.claim.status == EffectClaimStatus.PROCESSING.value
    assert retry.claim.attempt_count == 2


def test_digest_is_sha256_only() -> None:
    digest = effect_digest(b"sensitive payload")
    assert len(digest) == 64
    assert digest != "sensitive payload"
    int(digest, 16)
