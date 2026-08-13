"""Durable idempotency claims for externally triggered effects."""

import uuid
from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EffectClaimStatus(str, Enum):
    """Lifecycle of an effect execution."""

    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class EffectClaim(Base):
    """A privacy-preserving, scope-isolated effect execution claim."""

    __tablename__ = "effect_claims"
    __table_args__ = (
        UniqueConstraint("scope_key", "namespace", "digest", name="uq_effect_claim_identity"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    scope_key: Mapped[str] = mapped_column(String(64), nullable=False)
    namespace: Mapped[str] = mapped_column(String(100), nullable=False)
    digest: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    first_attempt_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    last_attempt_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    response: Mapped[str | None] = mapped_column(Text)
    provider_ref: Mapped[str | None] = mapped_column(String(255))
