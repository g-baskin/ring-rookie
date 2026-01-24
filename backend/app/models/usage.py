"""Usage tracking models for Chat Champ billing.

Tracks message and token usage per agent for billing tiers:
- FREE: 50 messages/day
- PRO: 2,000 messages/day
- BUSINESS: 10,000 messages/day
- ENTERPRISE: Unlimited
"""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.agent import Agent


class BillingTier(str, Enum):
    """Billing tier with daily message limits."""

    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


# Daily message limits per tier
TIER_LIMITS: dict[BillingTier, int | None] = {
    BillingTier.FREE: 50,
    BillingTier.PRO: 2000,
    BillingTier.BUSINESS: 10000,
    BillingTier.ENTERPRISE: None,  # Unlimited
}


class UsageRecord(Base):
    """Daily usage tracking per agent.

    Records are aggregated by date to track:
    - Message count for billing tier limits
    - Token usage for cost analysis
    - Knowledge base storage for tier limits
    """

    __tablename__ = "usage_records"
    __table_args__ = (
        # Unique constraint: one record per agent per day
        Index(
            "ix_usage_records_agent_date",
            "agent_id",
            "usage_date",
            unique=True,
        ),
        # Fast lookup for daily usage checks
        Index("ix_usage_records_date", "usage_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Agent this usage belongs to",
    )

    # Date tracking (UTC date, no time component for aggregation)
    usage_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Date of usage (UTC, truncated to day)",
    )

    # Message metrics
    message_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of messages sent this day",
    )
    conversation_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of new conversations started this day",
    )

    # Token metrics
    prompt_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total prompt tokens consumed",
    )
    completion_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total completion tokens generated",
    )
    embedding_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total tokens used for embeddings",
    )

    # Storage metrics (in bytes)
    knowledge_base_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total knowledge base storage in bytes",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", lazy="selectin")

    @property
    def total_tokens(self) -> int:
        """Total tokens consumed (prompt + completion + embedding)."""
        return self.prompt_tokens + self.completion_tokens + self.embedding_tokens

    def __repr__(self) -> str:
        date_str = self.usage_date.strftime("%Y-%m-%d") if self.usage_date else "unknown"
        return (
            f"<UsageRecord(agent_id={self.agent_id}, date={date_str}, "
            f"messages={self.message_count}, tokens={self.total_tokens})>"
        )


class AgentBillingConfig(Base):
    """Billing configuration per agent.

    Stores the billing tier and any custom limits for an agent.
    """

    __tablename__ = "agent_billing_configs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="Agent this billing config belongs to",
    )

    # Billing tier
    tier: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=BillingTier.FREE.value,
        comment="Billing tier: free, pro, business, enterprise",
    )

    # Custom limits (override tier defaults if set)
    custom_message_limit: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Custom daily message limit (overrides tier default)",
    )
    custom_storage_limit_mb: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Custom storage limit in MB (overrides tier default)",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", lazy="selectin")

    def get_message_limit(self) -> int | None:
        """Get effective daily message limit.

        Returns None for unlimited (enterprise tier).
        """
        if self.custom_message_limit is not None:
            return self.custom_message_limit

        try:
            tier = BillingTier(self.tier)
            return TIER_LIMITS.get(tier)
        except ValueError:
            # Invalid tier, default to free
            return TIER_LIMITS[BillingTier.FREE]

    def __repr__(self) -> str:
        return f"<AgentBillingConfig(agent_id={self.agent_id}, tier={self.tier})>"
