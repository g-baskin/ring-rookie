"""Durable, privacy-minimized background work records."""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class WorkerItemStatus(str, Enum):
    QUEUED = "queued"
    LEASED = "leased"
    RETRY_WAIT = "retry_wait"
    COMPLETED = "completed"
    DEAD = "dead"


class WorkerItem(TimestampMixin, Base):
    __tablename__ = "worker_items"
    __table_args__ = (
        UniqueConstraint("scope_key", "namespace", "item_digest", name="uq_worker_item_identity"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    scope_key: Mapped[str] = mapped_column(String(64), nullable=False)
    namespace: Mapped[str] = mapped_column(String(100), nullable=False)
    item_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    payload_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=WorkerItemStatus.QUEUED.value
    )
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    max_age_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=86400)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    lease_owner: Mapped[str | None] = mapped_column(String(100))
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    trace_id: Mapped[str | None] = mapped_column(String(64))
    exception_type: Mapped[str | None] = mapped_column(String(100))
    last_error: Mapped[str | None] = mapped_column(String(512))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    dead_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    replay_actor: Mapped[str | None] = mapped_column(String(100))
    replay_reason: Mapped[str | None] = mapped_column(String(255))
    replayed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    age_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
