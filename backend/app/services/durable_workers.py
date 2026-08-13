"""Database-backed worker claims, retry policy, runner, and DLQ replay."""

import asyncio
import hashlib
import random
import re
from collections.abc import Callable
from contextlib import suppress
from datetime import UTC, datetime, timedelta
from typing import Protocol

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.worker_item import WorkerItem, WorkerItemStatus
from app.services.effect_claims import (
    ClaimDisposition,
    acquire_claim,
    complete_claim,
    effect_digest,
    fail_claim,
)

_SAFE_REF = re.compile(
    r"^(campaign-contact|contact|appointment|call|integration):[A-Za-z0-9_-]{1,180}$"
)
_SAFE_AUDIT = re.compile(r"^[A-Za-z0-9_.@-]{1,100}$")


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
        raise ValueError("payload reference must be an allowlisted opaque domain-type:identifier")
    return value


def redact_error(exc: BaseException) -> tuple[str, str]:
    """Persist no exception data: only bounded class identity and generic disposition."""
    kind = re.sub(r"[^A-Za-z0-9_.]", "", type(exc).__name__)[:100] or "Error"
    message = (
        "retryable provider failure" if is_retryable_exception(exc) else "non-retryable failure"
    )
    return kind, message


class WorkerHandler(Protocol):
    effect_namespace: str | None

    def effect_key(self, item: WorkerItem) -> str | None: ...

    async def __call__(self, item: WorkerItem) -> None: ...


class DurableWorkerStore:
    def __init__(
        self, session: AsyncSession, *, clock: Callable[[], datetime] | None = None
    ) -> None:
        self.session = session
        self.clock = clock or (lambda: datetime.now(UTC))

    async def enqueue(
        self,
        *,
        scope_key: str,
        namespace: str,
        item_key: str,
        payload_ref: str,
        max_attempts: int = 5,
        max_age_seconds: int = 86400,
    ) -> WorkerItem:
        if not scope_key.strip() or not namespace.strip():
            raise ValueError("scope and namespace are required")
        if max_attempts < 1 or max_age_seconds < 1:
            raise ValueError("positive retry limits are required")
        now = self.clock()
        item = WorkerItem(
            scope_key=scope_key,
            namespace=namespace,
            item_digest=item_digest(item_key),
            payload_ref=safe_payload_ref(payload_ref),
            available_at=now,
            age_started_at=now,
            max_attempts=max_attempts,
            max_age_seconds=max_age_seconds,
        )
        try:
            async with self.session.begin_nested():
                self.session.add(item)
                await self.session.flush()
        except IntegrityError:
            item = (
                await self.session.execute(
                    select(WorkerItem).where(
                        WorkerItem.scope_key == scope_key,
                        WorkerItem.namespace == namespace,
                        WorkerItem.item_digest == item_digest(item_key),
                    )
                )
            ).scalar_one()
        return item

    async def claim(
        self, *, scope_key: str, namespace: str, owner: str, lease_seconds: int = 60
    ) -> WorkerItem | None:
        """Claim within the caller's transaction; commit makes the lease visible atomically."""
        if not scope_key.strip() or not namespace.strip():
            raise ValueError("scope and namespace are required")
        now = self.clock()
        eligible = or_(
            WorkerItem.status.in_(
                [WorkerItemStatus.QUEUED.value, WorkerItemStatus.RETRY_WAIT.value]
            ),
            (WorkerItem.status == WorkerItemStatus.LEASED.value)
            & (WorkerItem.lease_expires_at <= now),
        )
        stmt = (
            select(WorkerItem)
            .where(
                WorkerItem.scope_key == scope_key,
                WorkerItem.namespace == namespace,
                WorkerItem.available_at <= now,
                eligible,
            )
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

    async def heartbeat(self, item: WorkerItem, *, owner: str, lease_seconds: int = 60) -> bool:
        if item.status != WorkerItemStatus.LEASED.value or item.lease_owner != owner:
            return False
        item.lease_expires_at = self.clock() + timedelta(seconds=lease_seconds)
        await self.session.flush()
        return True

    async def complete(self, item: WorkerItem, *, owner: str) -> bool:
        if item.status != WorkerItemStatus.LEASED.value or item.lease_owner != owner:
            return False
        item.status = WorkerItemStatus.COMPLETED.value
        item.completed_at = self.clock()
        item.lease_owner = None
        item.lease_expires_at = None
        await self.session.flush()
        return True

    async def fail(self, item: WorkerItem, exc: BaseException, *, delay: float = 0) -> None:
        now = self.clock()
        expired = now >= item.age_started_at + timedelta(seconds=item.max_age_seconds)
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

    async def replay(self, item_id: object, *, actor: str, reason: str) -> bool:
        if not _SAFE_AUDIT.fullmatch(actor) or not reason.strip():
            raise ValueError("safe operator actor and reason are required")
        item = (
            await self.session.execute(
                select(WorkerItem).where(WorkerItem.id == item_id).with_for_update()
            )
        ).scalar_one()
        if item.status == WorkerItemStatus.COMPLETED.value:
            raise ValueError("completed work cannot be replayed")
        if item.status != WorkerItemStatus.DEAD.value:
            return False
        now = self.clock()
        item.status = WorkerItemStatus.QUEUED.value
        item.available_at = now
        item.age_started_at = now
        item.attempt_count = 0
        item.dead_at = None
        item.replay_actor = actor
        item.replay_reason = "operator-requested replay"  # never persist free-form input
        item.replayed_at = now
        item.exception_type = None
        item.last_error = None
        await self.session.flush()
        return True


class DurableWorkerRunner:
    def __init__(
        self,
        sessions: async_sessionmaker[AsyncSession],
        *,
        scope_key: str,
        namespace: str,
        owner: str,
        handler: WorkerHandler,
        rng: Callable[[], float] = random.random,
    ) -> None:
        self.sessions = sessions
        self.scope_key = scope_key
        self.namespace = namespace
        self.owner = owner
        self.handler = handler
        self.rng = rng
        self._stop = asyncio.Event()
        self._active: set[asyncio.Task[None]] = set()

    async def run(self, poll_seconds: float = 1.0) -> None:
        while not self._stop.is_set():
            async with self.sessions() as session, session.begin():
                item = await DurableWorkerStore(session).claim(
                    scope_key=self.scope_key, namespace=self.namespace, owner=self.owner
                )
            if item is None:
                with suppress(TimeoutError):
                    await asyncio.wait_for(self._stop.wait(), poll_seconds)
                continue
            task = asyncio.create_task(self._handle(item.id))
            self._active.add(task)
            task.add_done_callback(self._active.discard)

    async def _handle(self, item_id: object) -> None:
        async with self.sessions() as session:
            item = (
                await session.execute(select(WorkerItem).where(WorkerItem.id == item_id))
            ).scalar_one()
            claim = None
            try:
                key = self.handler.effect_key(item)
                if self.handler.effect_namespace and key:
                    claim_result = await acquire_claim(
                        session,
                        scope_key=item.scope_key,
                        namespace=self.handler.effect_namespace,
                        digest=effect_digest(key),
                    )
                    if claim_result.disposition is not ClaimDisposition.ACQUIRED:
                        async with session.begin():
                            await DurableWorkerStore(session).complete(item, owner=self.owner)
                        return
                    claim = claim_result.claim
                await self.handler(item)
                if claim:
                    await complete_claim(session, claim, response="completed")
                async with session.begin():
                    await DurableWorkerStore(session).complete(item, owner=self.owner)
            except asyncio.CancelledError:
                if claim:
                    await fail_claim(session, claim)
                raise
            except Exception as exc:
                if claim:
                    await fail_claim(session, claim)
                async with session.begin():
                    await DurableWorkerStore(session).fail(
                        item, exc, delay=retry_delay(item.attempt_count, rng=self.rng)
                    )

    async def shutdown(self, grace_seconds: float = 10.0) -> None:
        self._stop.set()
        if not self._active:
            return
        _, pending = await asyncio.wait(self._active, timeout=grace_seconds)
        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
