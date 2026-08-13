"""Database-backed worker claims, retry policy, and DLQ replay."""

import asyncio
import hashlib
import random
import re
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.worker_item import WorkerItem, WorkerItemStatus

_SAFE_REF = re.compile(r"^[a-z][a-z0-9_-]{0,49}:[A-Za-z0-9_-]{1,180}$")


def item_digest(item_key: str) -> str:
    return hashlib.sha256(item_key.encode()).hexdigest()


def retry_delay(
    attempt: int, base: float = 1.0, cap: float = 300.0, rng: Callable[[], float] = random.random
) -> float:
    return float(rng() * min(cap, base * (2 ** max(0, attempt - 1))))


def is_retryable_exception(exc: BaseException) -> bool:
    return isinstance(exc, (TimeoutError, ConnectionError, asyncio.TimeoutError)) or bool(
        getattr(exc, "retryable", False)
    )


def safe_payload_ref(value: str) -> str:
    if not _SAFE_REF.fullmatch(value):
        raise ValueError("payload reference must be an opaque domain-type:identifier")
    return value


def redact_error(exc: BaseException) -> tuple[str, str]:
    """Persist no exception data: only bounded class identity and generic disposition."""
    return type(exc).__name__[:100], "retryable provider failure" if is_retryable_exception(
        exc
    ) else "non-retryable failure"


class DurableWorkerStore:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def claim(self, namespace: str, owner: str, lease_seconds: int = 60) -> WorkerItem | None:
        now = datetime.now(UTC)
        eligible = or_(
            WorkerItem.status.in_(
                [WorkerItemStatus.QUEUED.value, WorkerItemStatus.RETRY_WAIT.value]
            ),
            (WorkerItem.status == WorkerItemStatus.LEASED.value)
            & (WorkerItem.lease_expires_at <= now),
        )
        stmt = (
            select(WorkerItem)
            .where(WorkerItem.namespace == namespace, WorkerItem.available_at <= now, eligible)
            .order_by(WorkerItem.available_at, WorkerItem.created_at)
            .limit(1)
        )
        if self.session.bind and self.session.bind.dialect.name == "postgresql":
            stmt = stmt.with_for_update(skip_locked=True)
        item = (await self.session.execute(stmt)).scalar_one_or_none()
        if item is None:
            return None
        item.status = WorkerItemStatus.LEASED.value
        item.lease_owner = owner
        item.lease_expires_at = now + timedelta(seconds=lease_seconds)
        item.attempt_count += 1
        await self.session.flush()
        return item

    async def fail(self, item: WorkerItem, exc: BaseException, *, delay: float = 0) -> None:
        now = datetime.now(UTC)
        expired = now >= item.created_at + timedelta(seconds=item.max_age_seconds)
        exhausted = item.attempt_count >= item.max_attempts
        item.exception_type, item.last_error = redact_error(exc)
        item.lease_owner = None
        item.lease_expires_at = None
        if not is_retryable_exception(exc) or expired or exhausted:
            item.status = WorkerItemStatus.DEAD.value
            item.dead_at = item.dead_at or now
        else:
            item.status = WorkerItemStatus.RETRY_WAIT.value
            item.available_at = now + timedelta(seconds=delay)
        await self.session.flush()

    async def replay(self, item: WorkerItem, *, actor: str, reason: str) -> bool:
        if item.status == WorkerItemStatus.COMPLETED.value:
            raise ValueError("completed work cannot be replayed")
        if item.status != WorkerItemStatus.DEAD.value:
            return False
        if not actor.strip() or not reason.strip():
            raise ValueError("operator actor and reason are required")
        item.status = WorkerItemStatus.QUEUED.value
        item.available_at = datetime.now(UTC)
        item.dead_at = None
        item.replay_actor = actor[:100]
        item.replay_reason = reason[:255]
        item.exception_type = None
        item.last_error = None
        await self.session.flush()
        return True
