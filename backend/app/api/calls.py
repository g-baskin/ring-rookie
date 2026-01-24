"""Call history API routes."""

import csv
import io
import json
import re
import uuid
from datetime import datetime
from typing import Literal

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.auth import CurrentUser, user_id_to_uuid
from app.core.config import settings
from app.db.session import get_db
from app.models.call_record import CallRecord

router = APIRouter(prefix="/api/v1/calls", tags=["calls"])
logger = structlog.get_logger()

# Cost per minute estimate (OpenAI Realtime API)
COST_PER_MINUTE = 0.15

# Efficiency thresholds (words per minute)
EFFICIENT_WPM_THRESHOLD = 30
MODERATE_WPM_THRESHOLD = 15

# Minimum calls required for analysis
MIN_CALLS_FOR_ANALYSIS = 3


# =============================================================================
# Pydantic Models
# =============================================================================


class CallRecordResponse(BaseModel):
    """Call record response."""

    id: str
    provider: str
    provider_call_id: str
    agent_id: str | None
    agent_name: str | None = None
    contact_id: int | None
    contact_name: str | None = None
    workspace_id: str | None = None
    workspace_name: str | None = None
    direction: str
    status: str
    from_number: str
    to_number: str
    duration_seconds: int
    recording_url: str | None
    transcript: str | None
    started_at: datetime
    answered_at: datetime | None
    ended_at: datetime | None

    model_config = {"from_attributes": True}


class CallRecordListResponse(BaseModel):
    """Paginated call records response."""

    calls: list[CallRecordResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# =============================================================================
# Export Models
# =============================================================================


class ExportCallsRequest(BaseModel):
    """Request to export calls."""

    format: Literal["csv", "json"] = "csv"
    call_ids: list[str] | None = None
    agent_id: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    include_transcripts: bool = True


# =============================================================================
# Analysis Models
# =============================================================================


class AnalyzeCallsRequest(BaseModel):
    """Request to analyze calls."""

    call_ids: list[str] | None = None
    agent_id: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None


class CallAnalysisResponse(BaseModel):
    """Call analysis response with AI-generated insights."""

    total_calls_analyzed: int
    total_duration_seconds: int
    patterns: list[str]
    issues: list[str]
    suggestions: list[str]
    sample_improvements: str


# =============================================================================
# Analytics Models
# =============================================================================


class CallEfficiencyScore(BaseModel):
    """Efficiency score for a single call."""

    call_id: str
    agent_name: str | None
    duration_seconds: int
    transcript_length: int
    word_count: int
    turn_count: int
    words_per_minute: float
    efficiency_rating: Literal["efficient", "moderate", "wasteful"]
    started_at: datetime


class CallAnalyticsResponse(BaseModel):
    """Call analytics with efficiency metrics."""

    total_calls: int
    total_duration_seconds: int
    avg_duration_seconds: float

    efficiency_scores: list[CallEfficiencyScore]

    calls_by_efficiency: dict[str, int]
    avg_words_per_minute: float
    avg_turns_per_call: float

    estimated_cost_total: float
    estimated_cost_wasted: float


# =============================================================================
# Helper Functions
# =============================================================================


def calculate_efficiency(duration_seconds: int, word_count: int) -> str:
    """Calculate efficiency rating based on words per minute.

    Normal speech: 120-150 WPM
    Voice agents with pauses: 40-80 WPM expected
    """
    if duration_seconds == 0:
        return "efficient"

    words_per_minute = (word_count / duration_seconds) * 60

    if words_per_minute >= EFFICIENT_WPM_THRESHOLD:
        return "efficient"
    if words_per_minute >= MODERATE_WPM_THRESHOLD:
        return "moderate"
    return "wasteful"


def count_words(text: str | None) -> int:
    """Count words in text."""
    if not text:
        return 0
    return len(text.split())


def count_turns(transcript: str | None) -> int:
    """Count speaker turns in transcript.

    Looks for patterns like [Speaker]: or Speaker: at start of lines.
    """
    if not transcript:
        return 0
    # Match patterns like [Assistant]: or User: at start of lines
    turns = re.findall(r"^\s*\[?\w+\]?\s*:", transcript, re.MULTILINE)
    return len(turns)


def estimate_cost(duration_seconds: int) -> float:
    """Estimate cost based on duration."""
    return (duration_seconds / 60) * COST_PER_MINUTE


# =============================================================================
# Call History Endpoints
# =============================================================================


@router.get("", response_model=CallRecordListResponse)
async def list_calls(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    agent_id: str | None = Query(default=None, description="Filter by agent ID"),
    workspace_id: str | None = Query(default=None, description="Filter by workspace ID"),
    direction: str | None = Query(
        default=None, description="Filter by direction: inbound or outbound"
    ),
    status: str | None = Query(default=None, description="Filter by status"),
) -> CallRecordListResponse:
    """List call records for the current user.

    Args:
        current_user: Authenticated user
        db: Database session
        page: Page number (1-indexed)
        page_size: Number of records per page
        agent_id: Optional filter by agent ID
        direction: Optional filter by direction
        status: Optional filter by status

    Returns:
        Paginated list of call records
    """
    log = logger.bind(user_id=current_user.id)
    log.info("listing_calls", page=page, page_size=page_size)

    # Build query with eager loading to prevent N+1 queries
    user_uuid = user_id_to_uuid(current_user.id)
    query = (
        select(CallRecord)
        .where(CallRecord.user_id == user_uuid)
        .options(
            selectinload(CallRecord.agent),
            selectinload(CallRecord.contact),
            selectinload(CallRecord.workspace),
        )
    )

    # Apply filters
    if agent_id:
        query = query.where(CallRecord.agent_id == uuid.UUID(agent_id))
    if workspace_id:
        query = query.where(CallRecord.workspace_id == uuid.UUID(workspace_id))
    if direction:
        query = query.where(CallRecord.direction == direction)
    if status:
        query = query.where(CallRecord.status == status)

    # Get total count
    count_query = select(CallRecord.id).where(CallRecord.user_id == user_uuid)
    if agent_id:
        count_query = count_query.where(CallRecord.agent_id == uuid.UUID(agent_id))
    if workspace_id:
        count_query = count_query.where(CallRecord.workspace_id == uuid.UUID(workspace_id))
    if direction:
        count_query = count_query.where(CallRecord.direction == direction)
    if status:
        count_query = count_query.where(CallRecord.status == status)

    count_result = await db.execute(count_query)
    total = len(count_result.all())

    # Apply pagination and ordering
    offset = (page - 1) * page_size
    query = query.order_by(desc(CallRecord.started_at)).offset(offset).limit(page_size)

    result = await db.execute(query)
    records = result.scalars().all()

    # Build response with agent, contact, and workspace names
    calls = []
    for record in records:
        agent_name = None
        contact_name = None
        workspace_name = None

        if record.agent:
            agent_name = record.agent.name
        if record.contact:
            contact_name = f"{record.contact.first_name} {record.contact.last_name or ''}".strip()
        if record.workspace:
            workspace_name = record.workspace.name

        calls.append(
            CallRecordResponse(
                id=str(record.id),
                provider=record.provider,
                provider_call_id=record.provider_call_id,
                agent_id=str(record.agent_id) if record.agent_id else None,
                agent_name=agent_name,
                contact_id=record.contact_id,
                contact_name=contact_name,
                workspace_id=str(record.workspace_id) if record.workspace_id else None,
                workspace_name=workspace_name,
                direction=record.direction,
                status=record.status,
                from_number=record.from_number,
                to_number=record.to_number,
                duration_seconds=record.duration_seconds,
                recording_url=record.recording_url,
                transcript=record.transcript,
                started_at=record.started_at,
                answered_at=record.answered_at,
                ended_at=record.ended_at,
            )
        )

    total_pages = (total + page_size - 1) // page_size

    return CallRecordListResponse(
        calls=calls,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# =============================================================================
# Analytics Endpoint (must be before /{call_id} to avoid route conflict)
# =============================================================================


@router.get("/analytics", response_model=CallAnalyticsResponse)
async def get_call_analytics(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    agent_id: str | None = Query(default=None, description="Filter by agent ID"),
    date_from: datetime | None = Query(default=None, description="Filter from date"),
    date_to: datetime | None = Query(default=None, description="Filter to date"),
) -> CallAnalyticsResponse:
    """Get call analytics including duration vs content efficiency metrics.

    Args:
        current_user: Authenticated user
        db: Database session
        agent_id: Optional filter by agent ID
        date_from: Optional filter from date
        date_to: Optional filter to date

    Returns:
        Analytics with efficiency scores and cost estimates
    """
    log = logger.bind(user_id=current_user.id)
    log.info("getting_call_analytics")

    user_uuid = user_id_to_uuid(current_user.id)

    # Build query
    query = (
        select(CallRecord)
        .where(CallRecord.user_id == user_uuid)
        .options(selectinload(CallRecord.agent))
    )

    if agent_id:
        query = query.where(CallRecord.agent_id == uuid.UUID(agent_id))
    if date_from:
        query = query.where(CallRecord.started_at >= date_from)
    if date_to:
        query = query.where(CallRecord.started_at <= date_to)

    query = query.order_by(desc(CallRecord.started_at))

    result = await db.execute(query)
    records = result.scalars().all()

    log.info("analytics_calls_count", count=len(records))

    # Calculate efficiency scores
    efficiency_scores: list[CallEfficiencyScore] = []
    calls_by_efficiency = {"efficient": 0, "moderate": 0, "wasteful": 0}
    total_wpm = 0.0
    total_turns = 0

    for record in records:
        word_count = count_words(record.transcript)
        turn_count = count_turns(record.transcript)
        transcript_length = len(record.transcript) if record.transcript else 0

        wpm = (word_count / record.duration_seconds * 60) if record.duration_seconds > 0 else 0
        rating = calculate_efficiency(record.duration_seconds, word_count)

        efficiency_scores.append(
            CallEfficiencyScore(
                call_id=str(record.id),
                agent_name=record.agent.name if record.agent else None,
                duration_seconds=record.duration_seconds,
                transcript_length=transcript_length,
                word_count=word_count,
                turn_count=turn_count,
                words_per_minute=round(wpm, 1),
                efficiency_rating=rating,
                started_at=record.started_at,
            )
        )

        calls_by_efficiency[rating] += 1
        total_wpm += wpm
        total_turns += turn_count

    # Calculate aggregates
    total_calls = len(records)
    total_duration = sum(r.duration_seconds for r in records)
    avg_duration = total_duration / total_calls if total_calls > 0 else 0
    avg_wpm = total_wpm / total_calls if total_calls > 0 else 0
    avg_turns = total_turns / total_calls if total_calls > 0 else 0

    # Calculate costs
    total_cost = estimate_cost(total_duration)
    wasteful_duration = sum(
        s.duration_seconds for s in efficiency_scores if s.efficiency_rating == "wasteful"
    )
    wasted_cost = estimate_cost(wasteful_duration)

    return CallAnalyticsResponse(
        total_calls=total_calls,
        total_duration_seconds=total_duration,
        avg_duration_seconds=round(avg_duration, 1),
        efficiency_scores=efficiency_scores[:100],  # Limit to 100 for response size
        calls_by_efficiency=calls_by_efficiency,
        avg_words_per_minute=round(avg_wpm, 1),
        avg_turns_per_call=round(avg_turns, 1),
        estimated_cost_total=round(total_cost, 2),
        estimated_cost_wasted=round(wasted_cost, 2),
    )


@router.get("/{call_id}", response_model=CallRecordResponse)
async def get_call(
    call_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> CallRecordResponse:
    """Get a specific call record.

    Args:
        call_id: Call record ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Call record details
    """
    log = logger.bind(user_id=current_user.id, call_id=call_id)
    log.info("getting_call")

    user_uuid = user_id_to_uuid(current_user.id)
    result = await db.execute(
        select(CallRecord).where(
            CallRecord.id == uuid.UUID(call_id),
            CallRecord.user_id == user_uuid,
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="Call record not found")

    agent_name = None
    contact_name = None
    workspace_name = None

    if record.agent:
        agent_name = record.agent.name
    if record.contact:
        contact_name = f"{record.contact.first_name} {record.contact.last_name or ''}".strip()
    if record.workspace:
        workspace_name = record.workspace.name

    return CallRecordResponse(
        id=str(record.id),
        provider=record.provider,
        provider_call_id=record.provider_call_id,
        agent_id=str(record.agent_id) if record.agent_id else None,
        agent_name=agent_name,
        contact_id=record.contact_id,
        contact_name=contact_name,
        workspace_id=str(record.workspace_id) if record.workspace_id else None,
        workspace_name=workspace_name,
        direction=record.direction,
        status=record.status,
        from_number=record.from_number,
        to_number=record.to_number,
        duration_seconds=record.duration_seconds,
        recording_url=record.recording_url,
        transcript=record.transcript,
        started_at=record.started_at,
        answered_at=record.answered_at,
        ended_at=record.ended_at,
    )


@router.get("/agent/{agent_id}/stats")
async def get_agent_call_stats(
    agent_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, int | float]:
    """Get call statistics for an agent.

    Args:
        agent_id: Agent ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Call statistics for the agent
    """
    log = logger.bind(user_id=current_user.id, agent_id=agent_id)
    log.info("getting_agent_call_stats")

    user_uuid = user_id_to_uuid(current_user.id)
    # Get all calls for this agent
    result = await db.execute(
        select(CallRecord).where(
            CallRecord.agent_id == uuid.UUID(agent_id),
            CallRecord.user_id == user_uuid,
        )
    )
    records = result.scalars().all()

    total_calls = len(records)
    total_duration = sum(r.duration_seconds for r in records)
    completed_calls = sum(1 for r in records if r.status == "completed")
    inbound_calls = sum(1 for r in records if r.direction == "inbound")
    outbound_calls = sum(1 for r in records if r.direction == "outbound")

    avg_duration = total_duration / total_calls if total_calls > 0 else 0

    return {
        "total_calls": total_calls,
        "completed_calls": completed_calls,
        "inbound_calls": inbound_calls,
        "outbound_calls": outbound_calls,
        "total_duration_seconds": total_duration,
        "average_duration_seconds": round(avg_duration, 1),
    }


# =============================================================================
# Export Endpoint
# =============================================================================


@router.post("/export")
async def export_calls(
    request: ExportCallsRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Export calls as CSV or JSON.

    Args:
        request: Export options (format, filters, include_transcripts)
        current_user: Authenticated user
        db: Database session

    Returns:
        Streaming response with CSV or JSON data
    """
    log = logger.bind(user_id=current_user.id, format=request.format)
    log.info("exporting_calls")

    user_uuid = user_id_to_uuid(current_user.id)

    # Build query
    query = (
        select(CallRecord)
        .where(CallRecord.user_id == user_uuid)
        .options(
            selectinload(CallRecord.agent),
            selectinload(CallRecord.contact),
            selectinload(CallRecord.workspace),
        )
    )

    # Apply filters
    if request.call_ids:
        query = query.where(CallRecord.id.in_([uuid.UUID(cid) for cid in request.call_ids]))
    if request.agent_id:
        query = query.where(CallRecord.agent_id == uuid.UUID(request.agent_id))
    if request.date_from:
        query = query.where(CallRecord.started_at >= request.date_from)
    if request.date_to:
        query = query.where(CallRecord.started_at <= request.date_to)

    query = query.order_by(desc(CallRecord.started_at))

    result = await db.execute(query)
    records = result.scalars().all()

    log.info("exporting_calls_count", count=len(records))

    if request.format == "json":
        # Build JSON response
        export_data = []
        for record in records:
            data = {
                "id": str(record.id),
                "provider": record.provider,
                "agent_id": str(record.agent_id) if record.agent_id else None,
                "agent_name": record.agent.name if record.agent else None,
                "contact_id": record.contact_id,
                "contact_name": (
                    f"{record.contact.first_name} {record.contact.last_name or ''}".strip()
                    if record.contact
                    else None
                ),
                "direction": record.direction,
                "status": record.status,
                "from_number": record.from_number,
                "to_number": record.to_number,
                "duration_seconds": record.duration_seconds,
                "recording_url": record.recording_url,
                "started_at": record.started_at.isoformat(),
                "answered_at": record.answered_at.isoformat() if record.answered_at else None,
                "ended_at": record.ended_at.isoformat() if record.ended_at else None,
            }
            if request.include_transcripts:
                data["transcript"] = record.transcript
            export_data.append(data)

        json_str = json.dumps(export_data, indent=2)
        return StreamingResponse(
            iter([json_str]),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=calls_export.json"},
        )
    # Build CSV response
    output = io.StringIO()
    fieldnames = [
        "id",
        "agent_name",
        "contact_name",
        "direction",
        "status",
        "from_number",
        "to_number",
        "duration_seconds",
        "started_at",
        "ended_at",
    ]
    if request.include_transcripts:
        fieldnames.append("transcript")

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for record in records:
        row = {
            "id": str(record.id),
            "agent_name": record.agent.name if record.agent else "",
            "contact_name": (
                f"{record.contact.first_name} {record.contact.last_name or ''}".strip()
                if record.contact
                else ""
            ),
            "direction": record.direction,
            "status": record.status,
            "from_number": record.from_number,
            "to_number": record.to_number,
            "duration_seconds": record.duration_seconds,
            "started_at": record.started_at.isoformat(),
            "ended_at": record.ended_at.isoformat() if record.ended_at else "",
        }
        if request.include_transcripts:
            row["transcript"] = record.transcript or ""
        writer.writerow(row)

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=calls_export.csv"},
    )


# =============================================================================
# Analysis Endpoint
# =============================================================================


@router.post("/analyze", response_model=CallAnalysisResponse)
async def analyze_calls(
    request: AnalyzeCallsRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> CallAnalysisResponse:
    """Analyze calls using GPT-4 to generate improvement suggestions.

    Args:
        request: Analysis options (call_ids or agent_id filter)
        current_user: Authenticated user
        db: Database session

    Returns:
        Analysis with patterns, issues, and suggestions
    """
    log = logger.bind(user_id=current_user.id)
    log.info("analyzing_calls")

    user_uuid = user_id_to_uuid(current_user.id)

    # Build query
    query = (
        select(CallRecord)
        .where(CallRecord.user_id == user_uuid)
        .where(CallRecord.transcript.isnot(None))
        .options(selectinload(CallRecord.agent))
    )

    # Apply filters
    if request.call_ids:
        query = query.where(CallRecord.id.in_([uuid.UUID(cid) for cid in request.call_ids]))
    if request.agent_id:
        query = query.where(CallRecord.agent_id == uuid.UUID(request.agent_id))
    if request.date_from:
        query = query.where(CallRecord.started_at >= request.date_from)
    if request.date_to:
        query = query.where(CallRecord.started_at <= request.date_to)

    # Limit to reasonable number for analysis
    query = query.order_by(desc(CallRecord.started_at)).limit(50)

    result = await db.execute(query)
    records = result.scalars().all()

    if len(records) < MIN_CALLS_FOR_ANALYSIS:
        raise HTTPException(
            status_code=400,
            detail=f"At least {MIN_CALLS_FOR_ANALYSIS} calls with transcripts are required for analysis",
        )

    log.info("analyzing_calls_count", count=len(records))

    # Prepare transcripts for analysis
    transcripts_text = ""
    for i, record in enumerate(records[:20], 1):  # Limit to 20 for context window
        agent_name = record.agent.name if record.agent else "Unknown"
        duration = record.duration_seconds
        transcripts_text += f"\n--- Call {i} (Agent: {agent_name}, Duration: {duration}s) ---\n"
        transcripts_text += record.transcript[:2000] if record.transcript else ""
        transcripts_text += "\n"

    # Call GPT-4 for analysis
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    analysis_prompt = f"""Analyze these voice agent call transcripts and provide insights to help improve the voice agent.

Return your analysis in the following JSON format:
{{
    "patterns": ["pattern1", "pattern2", ...],
    "issues": ["issue1", "issue2", ...],
    "suggestions": ["suggestion1", "suggestion2", ...],
    "sample_improvements": "Suggested system prompt improvements or greeting changes..."
}}

Where:
- patterns: Common successful conversation patterns you observe (3-5 items)
- issues: Problems identified like long silences, user confusion, repetitive responses, calls ending abruptly (3-5 items)
- suggestions: Specific actionable improvements for the voice agent (3-5 items)
- sample_improvements: A paragraph with concrete suggested changes to the system prompt or greeting

Transcripts to analyze:
{transcripts_text}

Respond ONLY with valid JSON, no additional text."""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at analyzing voice agent conversations and providing actionable improvements. Respond only with valid JSON.",
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

    total_duration = sum(r.duration_seconds for r in records)

    return CallAnalysisResponse(
        total_calls_analyzed=len(records),
        total_duration_seconds=total_duration,
        patterns=analysis.get("patterns", []),
        issues=analysis.get("issues", []),
        suggestions=analysis.get("suggestions", []),
        sample_improvements=analysis.get("sample_improvements", ""),
    )
