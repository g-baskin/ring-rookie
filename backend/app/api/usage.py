"""Usage and billing API for Chat Champ.

Provides endpoints for querying usage statistics and managing billing tiers.
"""

import uuid
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.agent import Agent
from app.models.usage import TIER_LIMITS, BillingTier
from app.models.user import User
from app.services.usage import STORAGE_LIMITS, UsageService

router = APIRouter(prefix="/api/usage", tags=["usage"])
logger = structlog.get_logger()


class UsageStatusResponse(BaseModel):
    """Current usage status for an agent."""

    agent_id: str
    tier: str
    message_count: int
    message_limit: int | None
    remaining: int | None
    usage_percentage: float | None
    is_allowed: bool
    reset_at: str


class UsageSummaryResponse(BaseModel):
    """Usage summary for billing period."""

    agent_id: str
    period_days: int
    tier: str
    total_messages: int
    total_conversations: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_embedding_tokens: int
    total_tokens: int
    max_storage_bytes: int
    days_active: int


class DailyUsageItem(BaseModel):
    """Daily usage breakdown."""

    date: str
    message_count: int
    conversation_count: int
    prompt_tokens: int
    completion_tokens: int
    embedding_tokens: int
    total_tokens: int


class UpdateTierRequest(BaseModel):
    """Request to update billing tier."""

    tier: str = Field(..., description="Billing tier: free, pro, business, enterprise")
    custom_message_limit: int | None = Field(None, description="Custom daily message limit")
    custom_storage_limit_mb: int | None = Field(None, description="Custom storage limit in MB")


class TierInfoResponse(BaseModel):
    """Information about a billing tier."""

    tier: str
    daily_message_limit: int | None
    storage_limit_mb: int | None


async def _verify_agent_ownership(
    agent_id: str,
    user: User,
    db: AsyncSession,
) -> Agent:
    """Verify user owns the agent."""
    from sqlalchemy import select

    result = await db.execute(
        select(Agent).where(
            Agent.id == uuid.UUID(agent_id),
            Agent.user_id == user.id,
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.get("/tiers")
async def list_billing_tiers() -> list[TierInfoResponse]:
    """List all available billing tiers and their limits."""
    return [
        TierInfoResponse(
            tier=tier.value,
            daily_message_limit=TIER_LIMITS[tier],
            storage_limit_mb=STORAGE_LIMITS[tier],
        )
        for tier in BillingTier
    ]


@router.get("/agent/{agent_id}/status", response_model=UsageStatusResponse)
async def get_usage_status(
    agent_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UsageStatusResponse:
    """Get current usage status for an agent.

    Returns message count, limits, and whether more messages are allowed.
    """
    await _verify_agent_ownership(agent_id, user, db)

    service = UsageService(db)
    status = await service.check_usage_limit(uuid.UUID(agent_id))

    return UsageStatusResponse(
        agent_id=str(status.agent_id),
        tier=status.tier.value,
        message_count=status.message_count,
        message_limit=status.message_limit,
        remaining=status.remaining,
        usage_percentage=status.usage_percentage,
        is_allowed=status.is_allowed,
        reset_at=status.reset_at.isoformat(),
    )


@router.get("/agent/{agent_id}/summary", response_model=UsageSummaryResponse)
async def get_usage_summary(
    agent_id: str,
    days: int = 30,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UsageSummaryResponse:
    """Get usage summary for an agent.

    Returns aggregated statistics for the specified period (default 30 days).
    """
    await _verify_agent_ownership(agent_id, user, db)

    service = UsageService(db)
    summary = await service.get_usage_summary(uuid.UUID(agent_id), days=days)

    return UsageSummaryResponse(**summary)


@router.get("/agent/{agent_id}/daily")
async def get_daily_usage(
    agent_id: str,
    days: int = 7,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[DailyUsageItem]:
    """Get daily usage breakdown for charts.

    Returns daily stats for the specified period (default 7 days).
    """
    await _verify_agent_ownership(agent_id, user, db)

    service = UsageService(db)
    daily = await service.get_daily_usage(uuid.UUID(agent_id), days=days)

    return [DailyUsageItem(**item) for item in daily]


@router.get("/agent/{agent_id}/billing")
async def get_billing_config(
    agent_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get billing configuration for an agent."""
    await _verify_agent_ownership(agent_id, user, db)

    service = UsageService(db)
    config = await service.get_billing_config(uuid.UUID(agent_id))

    return {
        "agent_id": str(config.agent_id),
        "tier": config.tier,
        "custom_message_limit": config.custom_message_limit,
        "custom_storage_limit_mb": config.custom_storage_limit_mb,
        "effective_message_limit": config.get_message_limit(),
        "created_at": config.created_at.isoformat(),
        "updated_at": config.updated_at.isoformat(),
    }


@router.put("/agent/{agent_id}/billing")
async def update_billing_config(
    agent_id: str,
    request: UpdateTierRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Update billing tier for an agent.

    Note: In production, tier upgrades should go through a payment processor.
    This endpoint is for admin/testing purposes.
    """
    await _verify_agent_ownership(agent_id, user, db)

    # Validate tier
    try:
        tier = BillingTier(request.tier)
    except ValueError as err:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier. Must be one of: {[t.value for t in BillingTier]}",
        ) from err

    service = UsageService(db)
    config = await service.update_tier(
        agent_id=uuid.UUID(agent_id),
        tier=tier,
        custom_message_limit=request.custom_message_limit,
        custom_storage_limit_mb=request.custom_storage_limit_mb,
    )
    await db.commit()

    logger.info(
        "billing_tier_updated",
        agent_id=agent_id,
        tier=tier.value,
        user_id=user.id,
    )

    return {
        "agent_id": str(config.agent_id),
        "tier": config.tier,
        "custom_message_limit": config.custom_message_limit,
        "custom_storage_limit_mb": config.custom_storage_limit_mb,
        "effective_message_limit": config.get_message_limit(),
        "updated_at": config.updated_at.isoformat(),
    }
