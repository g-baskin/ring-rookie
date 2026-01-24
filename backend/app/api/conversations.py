"""Conversation history API routes for Chat Champ dashboard.

Provides authenticated endpoints to view, export, and analyze
chat conversations from the dashboard.
"""

import csv
import io
import json
import uuid
from datetime import datetime
from typing import Any, Literal

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.auth import CurrentUser
from app.core.config import settings
from app.db.session import get_db
from app.models.agent import Agent
from app.models.conversation import Conversation

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])
logger = structlog.get_logger()

# Cost estimates for GPT-4o-mini (per 1M tokens)
INPUT_COST_PER_MILLION = 0.15
OUTPUT_COST_PER_MILLION = 0.60

# Efficiency thresholds
EFFICIENT_MESSAGES_THRESHOLD = 5
MODERATE_MESSAGES_THRESHOLD = 2

# Minimum conversations for analysis
MIN_CONVERSATIONS_FOR_ANALYSIS = 3


# =============================================================================
# Pydantic Models
# =============================================================================


class MessageResponse(BaseModel):
    """Message response."""

    id: str
    role: str
    content: str
    input_tokens: int
    output_tokens: int
    model: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    """Conversation response."""

    id: str
    agent_id: str
    agent_name: str | None = None
    session_id: str
    status: str
    message_count: int
    total_tokens: int
    started_at: datetime
    ended_at: datetime | None
    last_message_at: datetime | None
    messages: list[MessageResponse] | None = None

    model_config = {"from_attributes": True}


class ConversationListResponse(BaseModel):
    """Paginated conversations response."""

    conversations: list[ConversationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ExportConversationsRequest(BaseModel):
    """Request to export conversations."""

    format: Literal["csv", "json"] = "csv"
    conversation_ids: list[str] | None = None
    agent_id: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    include_messages: bool = True


class AnalyzeConversationsRequest(BaseModel):
    """Request to analyze conversations."""

    conversation_ids: list[str] | None = None
    agent_id: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None


class ConversationAnalysisResponse(BaseModel):
    """Conversation analysis response with AI-generated insights."""

    total_conversations_analyzed: int
    total_messages: int
    total_tokens: int
    patterns: list[str]
    issues: list[str]
    suggestions: list[str]
    sample_improvements: str


class ConversationEfficiencyScore(BaseModel):
    """Efficiency score for a single conversation."""

    conversation_id: str
    agent_name: str | None
    message_count: int
    total_tokens: int
    input_tokens: int
    output_tokens: int
    duration_seconds: int | None
    efficiency_rating: Literal["efficient", "moderate", "wasteful"]
    started_at: datetime


class ConversationAnalyticsResponse(BaseModel):
    """Conversation analytics with efficiency metrics."""

    total_conversations: int
    total_messages: int
    total_tokens: int
    avg_messages_per_conversation: float
    avg_tokens_per_conversation: float

    efficiency_scores: list[ConversationEfficiencyScore]

    conversations_by_efficiency: dict[str, int]
    avg_duration_seconds: float | None

    estimated_cost_total: float
    estimated_cost_wasted: float


# =============================================================================
# Helper Functions
# =============================================================================


def calculate_efficiency(message_count: int) -> str:
    """Calculate efficiency rating based on message count.

    Short conversations with few messages might indicate:
    - User didn't get the answer they needed
    - Bot confused the user
    - User abandoned the chat
    """
    if message_count >= EFFICIENT_MESSAGES_THRESHOLD:
        return "efficient"
    if message_count >= MODERATE_MESSAGES_THRESHOLD:
        return "moderate"
    return "wasteful"


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """Estimate cost based on token usage."""
    input_cost = (input_tokens / 1_000_000) * INPUT_COST_PER_MILLION
    output_cost = (output_tokens / 1_000_000) * OUTPUT_COST_PER_MILLION
    return input_cost + output_cost


# =============================================================================
# List Conversations Endpoint
# =============================================================================


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    agent_id: str | None = Query(default=None, description="Filter by agent ID"),
    status: str | None = Query(default=None, description="Filter by status"),
) -> ConversationListResponse:
    """List chat conversations for the current user's agents."""
    log = logger.bind(user_id=current_user.id)
    log.info("listing_conversations", page=page, page_size=page_size)

    # Get user's agents first
    agents_query = select(Agent.id).where(Agent.user_id == current_user.id)
    agents_result = await db.execute(agents_query)
    agent_ids = [row[0] for row in agents_result.all()]

    if not agent_ids:
        return ConversationListResponse(
            conversations=[],
            total=0,
            page=page,
            page_size=page_size,
            total_pages=0,
        )

    # Build query for conversations
    query = (
        select(Conversation)
        .where(Conversation.agent_id.in_(agent_ids))
        .options(selectinload(Conversation.agent))
    )

    # Apply filters
    if agent_id:
        query = query.where(Conversation.agent_id == uuid.UUID(agent_id))
    if status:
        query = query.where(Conversation.status == status)

    # Get total count
    count_query = select(func.count(Conversation.id)).where(Conversation.agent_id.in_(agent_ids))
    if agent_id:
        count_query = count_query.where(Conversation.agent_id == uuid.UUID(agent_id))
    if status:
        count_query = count_query.where(Conversation.status == status)

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Apply pagination and ordering
    offset = (page - 1) * page_size
    query = query.order_by(desc(Conversation.last_message_at)).offset(offset).limit(page_size)

    result = await db.execute(query)
    records = result.scalars().all()

    # Build response
    conversations = []
    for record in records:
        conversations.append(
            ConversationResponse(
                id=str(record.id),
                agent_id=str(record.agent_id),
                agent_name=record.agent.name if record.agent else None,
                session_id=record.session_id,
                status=record.status,
                message_count=record.message_count,
                total_tokens=record.total_tokens,
                started_at=record.started_at,
                ended_at=record.ended_at,
                last_message_at=record.last_message_at,
            )
        )

    total_pages = (total + page_size - 1) // page_size

    return ConversationListResponse(
        conversations=conversations,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# =============================================================================
# Analytics Endpoint (must be before /{conversation_id})
# =============================================================================


@router.get("/analytics", response_model=ConversationAnalyticsResponse)
async def get_conversation_analytics(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    agent_id: str | None = Query(default=None, description="Filter by agent ID"),
    date_from: datetime | None = Query(default=None, description="Filter from date"),
    date_to: datetime | None = Query(default=None, description="Filter to date"),
) -> ConversationAnalyticsResponse:
    """Get conversation analytics including efficiency metrics."""
    log = logger.bind(user_id=current_user.id)
    log.info("getting_conversation_analytics")

    # Get user's agents
    agents_query = select(Agent.id).where(Agent.user_id == current_user.id)
    agents_result = await db.execute(agents_query)
    agent_ids = [row[0] for row in agents_result.all()]

    if not agent_ids:
        return ConversationAnalyticsResponse(
            total_conversations=0,
            total_messages=0,
            total_tokens=0,
            avg_messages_per_conversation=0,
            avg_tokens_per_conversation=0,
            efficiency_scores=[],
            conversations_by_efficiency={"efficient": 0, "moderate": 0, "wasteful": 0},
            avg_duration_seconds=None,
            estimated_cost_total=0,
            estimated_cost_wasted=0,
        )

    # Build query
    query = (
        select(Conversation)
        .where(Conversation.agent_id.in_(agent_ids))
        .options(
            selectinload(Conversation.agent),
            selectinload(Conversation.messages),
        )
    )

    if agent_id:
        query = query.where(Conversation.agent_id == uuid.UUID(agent_id))
    if date_from:
        query = query.where(Conversation.started_at >= date_from)
    if date_to:
        query = query.where(Conversation.started_at <= date_to)

    query = query.order_by(desc(Conversation.started_at))

    result = await db.execute(query)
    records = result.scalars().all()

    log.info("analytics_conversations_count", count=len(records))

    # Calculate efficiency scores
    efficiency_scores: list[ConversationEfficiencyScore] = []
    conversations_by_efficiency = {"efficient": 0, "moderate": 0, "wasteful": 0}
    total_messages = 0
    total_tokens = 0
    total_input_tokens = 0
    total_output_tokens = 0
    total_duration = 0
    duration_count = 0

    for record in records:
        # Calculate tokens from messages
        input_tokens = sum(m.input_tokens for m in record.messages)
        output_tokens = sum(m.output_tokens for m in record.messages)

        # Calculate duration if ended
        duration_seconds = None
        if record.ended_at and record.started_at:
            duration_seconds = int((record.ended_at - record.started_at).total_seconds())
            total_duration += duration_seconds
            duration_count += 1

        rating = calculate_efficiency(record.message_count)

        efficiency_scores.append(
            ConversationEfficiencyScore(
                conversation_id=str(record.id),
                agent_name=record.agent.name if record.agent else None,
                message_count=record.message_count,
                total_tokens=record.total_tokens,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_seconds=duration_seconds,
                efficiency_rating=rating,
                started_at=record.started_at,
            )
        )

        conversations_by_efficiency[rating] += 1
        total_messages += record.message_count
        total_tokens += record.total_tokens
        total_input_tokens += input_tokens
        total_output_tokens += output_tokens

    # Calculate aggregates
    total_conversations = len(records)
    avg_messages = total_messages / total_conversations if total_conversations > 0 else 0
    avg_tokens = total_tokens / total_conversations if total_conversations > 0 else 0
    avg_duration = total_duration / duration_count if duration_count > 0 else None

    # Calculate costs
    total_cost = estimate_cost(total_input_tokens, total_output_tokens)
    wasteful_input = sum(
        s.input_tokens for s in efficiency_scores if s.efficiency_rating == "wasteful"
    )
    wasteful_output = sum(
        s.output_tokens for s in efficiency_scores if s.efficiency_rating == "wasteful"
    )
    wasted_cost = estimate_cost(wasteful_input, wasteful_output)

    return ConversationAnalyticsResponse(
        total_conversations=total_conversations,
        total_messages=total_messages,
        total_tokens=total_tokens,
        avg_messages_per_conversation=round(avg_messages, 1),
        avg_tokens_per_conversation=round(avg_tokens, 1),
        efficiency_scores=efficiency_scores[:100],
        conversations_by_efficiency=conversations_by_efficiency,
        avg_duration_seconds=round(avg_duration, 1) if avg_duration else None,
        estimated_cost_total=round(total_cost, 4),
        estimated_cost_wasted=round(wasted_cost, 4),
    )


# =============================================================================
# Get Single Conversation
# =============================================================================


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> ConversationResponse:
    """Get a specific conversation with messages."""
    log = logger.bind(user_id=current_user.id, conversation_id=conversation_id)
    log.info("getting_conversation")

    # Get user's agents
    agents_query = select(Agent.id).where(Agent.user_id == current_user.id)
    agents_result = await db.execute(agents_query)
    agent_ids = [row[0] for row in agents_result.all()]

    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.id == uuid.UUID(conversation_id),
            Conversation.agent_id.in_(agent_ids),
        )
        .options(
            selectinload(Conversation.agent),
            selectinload(Conversation.messages),
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = [
        MessageResponse(
            id=str(m.id),
            role=m.role,
            content=m.content,
            input_tokens=m.input_tokens,
            output_tokens=m.output_tokens,
            model=m.model,
            created_at=m.created_at,
        )
        for m in record.messages
    ]

    return ConversationResponse(
        id=str(record.id),
        agent_id=str(record.agent_id),
        agent_name=record.agent.name if record.agent else None,
        session_id=record.session_id,
        status=record.status,
        message_count=record.message_count,
        total_tokens=record.total_tokens,
        started_at=record.started_at,
        ended_at=record.ended_at,
        last_message_at=record.last_message_at,
        messages=messages,
    )


# =============================================================================
# Export Endpoint
# =============================================================================


@router.post("/export")
async def export_conversations(
    request: ExportConversationsRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Export conversations as CSV or JSON."""
    log = logger.bind(user_id=current_user.id, format=request.format)
    log.info("exporting_conversations")

    # Get user's agents
    agents_query = select(Agent.id).where(Agent.user_id == current_user.id)
    agents_result = await db.execute(agents_query)
    agent_ids = [row[0] for row in agents_result.all()]

    # Build query
    query = (
        select(Conversation)
        .where(Conversation.agent_id.in_(agent_ids))
        .options(
            selectinload(Conversation.agent),
            selectinload(Conversation.messages),
        )
    )

    # Apply filters
    if request.conversation_ids:
        query = query.where(
            Conversation.id.in_([uuid.UUID(cid) for cid in request.conversation_ids])
        )
    if request.agent_id:
        query = query.where(Conversation.agent_id == uuid.UUID(request.agent_id))
    if request.date_from:
        query = query.where(Conversation.started_at >= request.date_from)
    if request.date_to:
        query = query.where(Conversation.started_at <= request.date_to)

    query = query.order_by(desc(Conversation.started_at))

    result = await db.execute(query)
    records = result.scalars().all()

    log.info("exporting_conversations_count", count=len(records))

    if request.format == "json":
        export_data = []
        for record in records:
            data: dict[str, Any] = {
                "id": str(record.id),
                "agent_id": str(record.agent_id),
                "agent_name": record.agent.name if record.agent else None,
                "session_id": record.session_id,
                "status": record.status,
                "message_count": record.message_count,
                "total_tokens": record.total_tokens,
                "started_at": record.started_at.isoformat(),
                "ended_at": record.ended_at.isoformat() if record.ended_at else None,
            }
            if request.include_messages:
                data["messages"] = [
                    {
                        "role": m.role,
                        "content": m.content,
                        "created_at": m.created_at.isoformat(),
                    }
                    for m in record.messages
                ]
            export_data.append(data)

        json_str = json.dumps(export_data, indent=2)
        return StreamingResponse(
            iter([json_str]),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=conversations_export.json"},
        )

    # Build CSV response
    output = io.StringIO()
    fieldnames = [
        "id",
        "agent_name",
        "session_id",
        "status",
        "message_count",
        "total_tokens",
        "started_at",
        "ended_at",
    ]
    if request.include_messages:
        fieldnames.append("transcript")

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for record in records:
        row = {
            "id": str(record.id),
            "agent_name": record.agent.name if record.agent else "",
            "session_id": record.session_id,
            "status": record.status,
            "message_count": record.message_count,
            "total_tokens": record.total_tokens,
            "started_at": record.started_at.isoformat(),
            "ended_at": record.ended_at.isoformat() if record.ended_at else "",
        }
        if request.include_messages:
            transcript = "\n".join(
                f"[{m.role}]: {m.content}" for m in record.messages
            )
            row["transcript"] = transcript
        writer.writerow(row)

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=conversations_export.csv"},
    )


# =============================================================================
# Analysis Endpoint
# =============================================================================


@router.post("/analyze", response_model=ConversationAnalysisResponse)
async def analyze_conversations(
    request: AnalyzeConversationsRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> ConversationAnalysisResponse:
    """Analyze conversations using GPT-4 to generate improvement suggestions."""
    log = logger.bind(user_id=current_user.id)
    log.info("analyzing_conversations")

    # Get user's agents
    agents_query = select(Agent.id).where(Agent.user_id == current_user.id)
    agents_result = await db.execute(agents_query)
    agent_ids = [row[0] for row in agents_result.all()]

    # Build query
    query = (
        select(Conversation)
        .where(Conversation.agent_id.in_(agent_ids))
        .where(Conversation.message_count > 0)
        .options(
            selectinload(Conversation.agent),
            selectinload(Conversation.messages),
        )
    )

    if request.conversation_ids:
        query = query.where(
            Conversation.id.in_([uuid.UUID(cid) for cid in request.conversation_ids])
        )
    if request.agent_id:
        query = query.where(Conversation.agent_id == uuid.UUID(request.agent_id))
    if request.date_from:
        query = query.where(Conversation.started_at >= request.date_from)
    if request.date_to:
        query = query.where(Conversation.started_at <= request.date_to)

    query = query.order_by(desc(Conversation.started_at)).limit(50)

    result = await db.execute(query)
    records = result.scalars().all()

    if len(records) < MIN_CONVERSATIONS_FOR_ANALYSIS:
        raise HTTPException(
            status_code=400,
            detail=f"At least {MIN_CONVERSATIONS_FOR_ANALYSIS} conversations with messages are required for analysis",
        )

    log.info("analyzing_conversations_count", count=len(records))

    # Prepare transcripts for analysis
    transcripts_text = ""
    total_messages = 0
    total_tokens = 0

    for i, record in enumerate(records[:20], 1):
        agent_name = record.agent.name if record.agent else "Unknown"
        transcripts_text += f"\n--- Conversation {i} (Agent: {agent_name}, Messages: {record.message_count}) ---\n"
        for msg in record.messages[:20]:
            transcripts_text += f"[{msg.role}]: {msg.content[:500]}\n"
        transcripts_text += "\n"
        total_messages += record.message_count
        total_tokens += record.total_tokens

    # Call GPT-4 for analysis
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    analysis_prompt = f"""Analyze these chatbot conversation transcripts and provide insights to help improve the chat agent.

Return your analysis in the following JSON format:
{{
    "patterns": ["pattern1", "pattern2", ...],
    "issues": ["issue1", "issue2", ...],
    "suggestions": ["suggestion1", "suggestion2", ...],
    "sample_improvements": "Suggested system prompt improvements..."
}}

Where:
- patterns: Common successful conversation patterns you observe (3-5 items)
- issues: Problems identified like confusion, unanswered questions, abrupt endings (3-5 items)
- suggestions: Specific actionable improvements for the chat agent (3-5 items)
- sample_improvements: A paragraph with concrete suggested changes to the system prompt

Transcripts to analyze:
{transcripts_text}

Respond ONLY with valid JSON, no additional text."""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at analyzing chatbot conversations and providing actionable improvements. Respond only with valid JSON.",
                },
                {"role": "user", "content": analysis_prompt},
            ],
            temperature=0.3,
            max_tokens=1500,
        )

        content = response.choices[0].message.content or "{}"

        # Clean markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]

        analysis = json.loads(content)
    except json.JSONDecodeError:
        log.exception("analysis_json_parse_error", content=content[:500] if content else "")
        analysis = {
            "patterns": ["Unable to parse analysis - please try again"],
            "issues": [],
            "suggestions": [],
            "sample_improvements": "",
        }
    except Exception as e:
        log.exception("analysis_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e!s}") from e

    return ConversationAnalysisResponse(
        total_conversations_analyzed=len(records),
        total_messages=total_messages,
        total_tokens=total_tokens,
        patterns=analysis.get("patterns", []),
        issues=analysis.get("issues", []),
        suggestions=analysis.get("suggestions", []),
        sample_improvements=analysis.get("sample_improvements", ""),
    )
