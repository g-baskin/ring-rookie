"""Authenticated CRUD and safe exports for lessons learned from test calls."""

import csv
import io
import json
import uuid
from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, user_id_to_uuid
from app.db.session import get_db
from app.models.agent import Agent
from app.models.call_record import CallRecord
from app.models.lesson_learned import LessonLearned
from app.models.workspace import AgentWorkspace, Workspace

router = APIRouter(prefix="/api/v1/agents/{agent_id}/lessons", tags=["lessons"])


class LessonFields(BaseModel):
    """Bounded plain-text fields shared by create and update operations."""

    title: str = Field(min_length=1, max_length=200)
    observation: str = Field(min_length=1, max_length=5000)
    recommended_action: str = Field(min_length=1, max_length=5000)
    status: Literal["active", "archived"] = "active"

    @field_validator("title", "observation", "recommended_action")
    @classmethod
    def strip_text(cls, value: str) -> str:
        """Reject whitespace-only values and persist normalized plain text."""
        normalized = value.strip()
        if not normalized:
            raise ValueError("must not be blank")
        return normalized


class CreateLessonRequest(LessonFields):
    """Create a lesson linked to a completed source call."""

    source_call_id: uuid.UUID


class UpdateLessonRequest(BaseModel):
    """Editable lesson fields; omitted values remain unchanged."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    observation: str | None = Field(default=None, min_length=1, max_length=5000)
    recommended_action: str | None = Field(default=None, min_length=1, max_length=5000)
    status: Literal["active", "archived"] | None = None

    @field_validator("title", "observation", "recommended_action")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        """Normalize supplied text and reject whitespace-only updates."""
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("must not be blank")
        return normalized


class LessonResponse(BaseModel):
    """Lesson representation without source transcript content."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    agent_id: uuid.UUID
    workspace_id: uuid.UUID | None
    source_call_id: uuid.UUID
    title: str
    observation: str
    recommended_action: str
    status: str
    created_at: datetime
    updated_at: datetime


async def _authorize_agent(
    agent_id: uuid.UUID,
    workspace_id: uuid.UUID | None,
    current_user: CurrentUser,
    db: AsyncSession,
) -> Agent:
    """Apply the same direct-owner/workspace-owner contract as Realtime."""
    agent = await db.scalar(select(Agent).where(Agent.id == agent_id))
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    if workspace_id is not None:
        access = await db.scalar(
            select(AgentWorkspace)
            .join(Workspace, Workspace.id == AgentWorkspace.workspace_id)
            .where(
                AgentWorkspace.agent_id == agent.id,
                AgentWorkspace.workspace_id == workspace_id,
                Workspace.user_id == current_user.id,
            )
        )
        if access is None:
            raise HTTPException(status_code=403, detail="Not authorized to access this agent")
    elif agent.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this agent")
    return agent


async def _owned_lesson(
    lesson_id: uuid.UUID,
    agent_id: uuid.UUID,
    workspace_id: uuid.UUID | None,
    current_user: CurrentUser,
    db: AsyncSession,
) -> LessonLearned:
    await _authorize_agent(agent_id, workspace_id, current_user, db)
    lesson = await db.scalar(
        select(LessonLearned).where(
            LessonLearned.id == lesson_id,
            LessonLearned.agent_id == agent_id,
            LessonLearned.user_id == user_id_to_uuid(current_user.id),
            LessonLearned.workspace_id == workspace_id,
        )
    )
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


async def _lesson_query(
    agent_id: uuid.UUID,
    workspace_id: uuid.UUID | None,
    current_user: CurrentUser,
    db: AsyncSession,
    lesson_ids: list[uuid.UUID] | None = None,
) -> list[LessonLearned]:
    await _authorize_agent(agent_id, workspace_id, current_user, db)
    statement = select(LessonLearned).where(
        LessonLearned.agent_id == agent_id,
        LessonLearned.user_id == user_id_to_uuid(current_user.id),
        LessonLearned.workspace_id == workspace_id,
    )
    if lesson_ids:
        statement = statement.where(LessonLearned.id.in_(lesson_ids))
    result = await db.scalars(statement.order_by(LessonLearned.created_at.desc()))
    return list(result.all())


@router.post("", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    agent_id: uuid.UUID,
    request: CreateLessonRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    workspace_id: uuid.UUID | None = None,
) -> LessonLearned:
    """Create a lesson only from an owned, completed Test Agent call."""
    await _authorize_agent(agent_id, workspace_id, current_user, db)
    user_uuid = user_id_to_uuid(current_user.id)
    source_call = await db.scalar(
        select(CallRecord).where(
            CallRecord.id == request.source_call_id,
            CallRecord.agent_id == agent_id,
            CallRecord.user_id == user_uuid,
            CallRecord.workspace_id == workspace_id,
            CallRecord.provider == "test",
            CallRecord.status == "completed",
        )
    )
    if source_call is None:
        raise HTTPException(
            status_code=400, detail="Source call is not an owned completed test call"
        )

    lesson = LessonLearned(
        user_id=user_uuid,
        agent_id=agent_id,
        workspace_id=workspace_id,
        source_call_id=source_call.id,
        title=request.title,
        observation=request.observation,
        recommended_action=request.recommended_action,
        status=request.status,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    return lesson


@router.get("", response_model=list[LessonResponse])
async def list_lessons(
    agent_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    workspace_id: uuid.UUID | None = None,
) -> list[LessonLearned]:
    """List lessons for one authorized agent context."""
    return await _lesson_query(agent_id, workspace_id, current_user, db)


@router.patch("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    agent_id: uuid.UUID,
    lesson_id: uuid.UUID,
    request: UpdateLessonRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    workspace_id: uuid.UUID | None = None,
) -> LessonLearned:
    """Update user-authored lesson fields without changing its source call."""
    lesson = await _owned_lesson(lesson_id, agent_id, workspace_id, current_user, db)
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(lesson, field, value)
    await db.commit()
    await db.refresh(lesson)
    return lesson


@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    agent_id: uuid.UUID,
    lesson_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    workspace_id: uuid.UUID | None = None,
) -> Response:
    """Delete the lesson only; its source call remains intact."""
    lesson = await _owned_lesson(lesson_id, agent_id, workspace_id, current_user, db)
    await db.delete(lesson)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _neutralize_csv(value: object) -> str:
    """Prevent spreadsheet formula execution after whitespace is skipped."""
    text = str(value) if value is not None else ""
    if text.lstrip().startswith(("=", "+", "-", "@")):
        return f"\t{text}"
    return text


def _export_rows(lessons: list[LessonLearned]) -> list[dict[str, str]]:
    return [
        {
            "id": str(lesson.id),
            "agent_id": str(lesson.agent_id),
            "workspace_id": str(lesson.workspace_id) if lesson.workspace_id else "",
            "source_call_id": str(lesson.source_call_id),
            "title": lesson.title,
            "observation": lesson.observation,
            "recommended_action": lesson.recommended_action,
            "status": lesson.status,
            "created_at": lesson.created_at.isoformat(),
            "updated_at": lesson.updated_at.isoformat(),
        }
        for lesson in lessons
    ]


LessonIds = Annotated[list[uuid.UUID] | None, Query(alias="lesson_id")]


@router.get("/export/csv")
async def export_lessons_csv(
    agent_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    workspace_id: uuid.UUID | None = None,
    lesson_ids: LessonIds = None,
) -> Response:
    """Download selected or all lessons as formula-neutralized CSV."""
    rows = _export_rows(await _lesson_query(agent_id, workspace_id, current_user, db, lesson_ids))
    output = io.StringIO(newline="")
    fieldnames = list(rows[0]) if rows else list(_export_rows.__annotations__)
    if not rows:
        fieldnames = [
            "id",
            "agent_id",
            "workspace_id",
            "source_call_id",
            "title",
            "observation",
            "recommended_action",
            "status",
            "created_at",
            "updated_at",
        ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows({key: _neutralize_csv(value) for key, value in row.items()} for row in rows)
    return Response(
        content=output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="lessons-{agent_id}.csv"'},
    )


@router.get("/export/json")
async def export_lessons_json(
    agent_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    workspace_id: uuid.UUID | None = None,
    lesson_ids: LessonIds = None,
) -> Response:
    """Download selected or all lesson fields without source transcripts."""
    rows = _export_rows(await _lesson_query(agent_id, workspace_id, current_user, db, lesson_ids))
    return Response(
        content=json.dumps(rows, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="lessons-{agent_id}.json"'},
    )
