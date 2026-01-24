"""Usage metering service for Chat Champ billing.

Handles:
- Checking usage limits before allowing chat messages
- Recording usage after each message
- Querying usage statistics for billing
"""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usage import (
    AgentBillingConfig,
    BillingTier,
    UsageRecord,
)

logger = structlog.get_logger()


@dataclass
class UsageStatus:
    """Current usage status for an agent."""

    agent_id: uuid.UUID
    tier: BillingTier
    message_count: int
    message_limit: int | None  # None = unlimited
    remaining: int | None  # None = unlimited
    is_allowed: bool
    reset_at: datetime  # When usage resets (midnight UTC)

    @property
    def usage_percentage(self) -> float | None:
        """Percentage of limit used (0-100), None if unlimited."""
        if self.message_limit is None:
            return None
        return min(100.0, (self.message_count / self.message_limit) * 100)


class UsageService:
    """Service for tracking and checking usage limits."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.log = logger.bind(service="usage")

    async def get_billing_config(self, agent_id: uuid.UUID) -> AgentBillingConfig:
        """Get billing config for agent, creating default if needed."""
        result = await self.db.execute(
            select(AgentBillingConfig).where(AgentBillingConfig.agent_id == agent_id)
        )
        config = result.scalar_one_or_none()

        if not config:
            # Create default free tier config
            config = AgentBillingConfig(
                agent_id=agent_id,
                tier=BillingTier.FREE.value,
            )
            self.db.add(config)
            await self.db.flush()
            self.log.info("created_default_billing_config", agent_id=str(agent_id))

        return config

    async def get_today_usage(self, agent_id: uuid.UUID) -> UsageRecord:
        """Get or create today's usage record for an agent."""
        today = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)

        result = await self.db.execute(
            select(UsageRecord).where(
                UsageRecord.agent_id == agent_id,
                UsageRecord.usage_date == today,
            )
        )
        record = result.scalar_one_or_none()

        if not record:
            # Create today's record
            record = UsageRecord(
                agent_id=agent_id,
                usage_date=today,
            )
            self.db.add(record)
            await self.db.flush()

        return record

    async def check_usage_limit(self, agent_id: uuid.UUID) -> UsageStatus:
        """Check if agent has remaining usage quota.

        Returns UsageStatus with is_allowed=True if message can be sent.
        """
        config = await self.get_billing_config(agent_id)
        record = await self.get_today_usage(agent_id)

        try:
            tier = BillingTier(config.tier)
        except ValueError:
            tier = BillingTier.FREE

        limit = config.get_message_limit()
        today = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        reset_at = today + timedelta(days=1)

        # Calculate remaining
        if limit is None:
            remaining = None
            is_allowed = True
        else:
            remaining = max(0, limit - record.message_count)
            is_allowed = remaining > 0

        return UsageStatus(
            agent_id=agent_id,
            tier=tier,
            message_count=record.message_count,
            message_limit=limit,
            remaining=remaining,
            is_allowed=is_allowed,
            reset_at=reset_at,
        )

    async def record_message(
        self,
        agent_id: uuid.UUID,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        is_new_conversation: bool = False,
    ) -> UsageRecord:
        """Record a message and token usage.

        Uses upsert for atomic increment to handle concurrent requests.
        """
        today = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)

        # Upsert with atomic increment
        stmt = insert(UsageRecord).values(
            agent_id=agent_id,
            usage_date=today,
            message_count=1,
            conversation_count=1 if is_new_conversation else 0,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=["agent_id", "usage_date"],
            set_={
                "message_count": UsageRecord.message_count + 1,
                "conversation_count": UsageRecord.conversation_count
                + (1 if is_new_conversation else 0),
                "prompt_tokens": UsageRecord.prompt_tokens + prompt_tokens,
                "completion_tokens": UsageRecord.completion_tokens + completion_tokens,
                "updated_at": datetime.now(UTC),
            },
        )

        await self.db.execute(stmt)
        await self.db.flush()

        # Return updated record
        return await self.get_today_usage(agent_id)

    async def record_embedding_tokens(
        self,
        agent_id: uuid.UUID,
        embedding_tokens: int,
    ) -> None:
        """Record embedding token usage (for knowledge base operations)."""
        today = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)

        stmt = insert(UsageRecord).values(
            agent_id=agent_id,
            usage_date=today,
            embedding_tokens=embedding_tokens,
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=["agent_id", "usage_date"],
            set_={
                "embedding_tokens": UsageRecord.embedding_tokens + embedding_tokens,
                "updated_at": datetime.now(UTC),
            },
        )

        await self.db.execute(stmt)

    async def record_storage_usage(
        self,
        agent_id: uuid.UUID,
        bytes_delta: int,
    ) -> None:
        """Record knowledge base storage change (positive or negative)."""
        today = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)

        stmt = insert(UsageRecord).values(
            agent_id=agent_id,
            usage_date=today,
            knowledge_base_bytes=max(0, bytes_delta),
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=["agent_id", "usage_date"],
            set_={
                "knowledge_base_bytes": func.greatest(
                    0, UsageRecord.knowledge_base_bytes + bytes_delta
                ),
                "updated_at": datetime.now(UTC),
            },
        )

        await self.db.execute(stmt)

    async def get_usage_summary(
        self,
        agent_id: uuid.UUID,
        days: int = 30,
    ) -> dict[str, str | int]:
        """Get usage summary for billing/analytics.

        Returns aggregated stats for the specified number of days.
        """
        since = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(
            days=days - 1
        )

        result = await self.db.execute(
            select(
                func.sum(UsageRecord.message_count).label("total_messages"),
                func.sum(UsageRecord.conversation_count).label("total_conversations"),
                func.sum(UsageRecord.prompt_tokens).label("total_prompt_tokens"),
                func.sum(UsageRecord.completion_tokens).label("total_completion_tokens"),
                func.sum(UsageRecord.embedding_tokens).label("total_embedding_tokens"),
                func.max(UsageRecord.knowledge_base_bytes).label("max_storage_bytes"),
                func.count(UsageRecord.id).label("days_active"),
            ).where(
                UsageRecord.agent_id == agent_id,
                UsageRecord.usage_date >= since,
            )
        )
        row = result.one()

        config = await self.get_billing_config(agent_id)

        return {
            "agent_id": str(agent_id),
            "period_days": days,
            "tier": config.tier,
            "total_messages": row.total_messages or 0,
            "total_conversations": row.total_conversations or 0,
            "total_prompt_tokens": row.total_prompt_tokens or 0,
            "total_completion_tokens": row.total_completion_tokens or 0,
            "total_embedding_tokens": row.total_embedding_tokens or 0,
            "total_tokens": (row.total_prompt_tokens or 0)
            + (row.total_completion_tokens or 0)
            + (row.total_embedding_tokens or 0),
            "max_storage_bytes": row.max_storage_bytes or 0,
            "days_active": row.days_active or 0,
        }

    async def get_daily_usage(
        self,
        agent_id: uuid.UUID,
        days: int = 7,
    ) -> list[dict[str, str | int]]:
        """Get daily usage breakdown for charts/analytics."""
        since = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(
            days=days - 1
        )

        result = await self.db.execute(
            select(UsageRecord)
            .where(
                UsageRecord.agent_id == agent_id,
                UsageRecord.usage_date >= since,
            )
            .order_by(UsageRecord.usage_date.asc())
        )
        records = result.scalars().all()

        return [
            {
                "date": record.usage_date.strftime("%Y-%m-%d"),
                "message_count": record.message_count,
                "conversation_count": record.conversation_count,
                "prompt_tokens": record.prompt_tokens,
                "completion_tokens": record.completion_tokens,
                "embedding_tokens": record.embedding_tokens,
                "total_tokens": record.total_tokens,
            }
            for record in records
        ]

    async def update_tier(
        self,
        agent_id: uuid.UUID,
        tier: BillingTier,
        custom_message_limit: int | None = None,
        custom_storage_limit_mb: int | None = None,
    ) -> AgentBillingConfig:
        """Update billing tier for an agent."""
        config = await self.get_billing_config(agent_id)
        config.tier = tier.value
        config.custom_message_limit = custom_message_limit
        config.custom_storage_limit_mb = custom_storage_limit_mb

        self.log.info(
            "updated_billing_tier",
            agent_id=str(agent_id),
            tier=tier.value,
            custom_limit=custom_message_limit,
        )

        return config


# Storage limits per tier (in MB)
STORAGE_LIMITS: dict[BillingTier, int | None] = {
    BillingTier.FREE: 0,  # No knowledge base on free tier
    BillingTier.PRO: 5,  # 5 MB
    BillingTier.BUSINESS: 50,  # 50 MB
    BillingTier.ENTERPRISE: None,  # Unlimited
}
