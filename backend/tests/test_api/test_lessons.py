"""API coverage for owned lessons and safe exports."""

import uuid
from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.auth import user_id_to_uuid
from app.models.agent import Agent
from app.models.call_record import CallRecord
from app.models.lesson_learned import LessonLearned
from app.models.user import User

pytestmark = pytest.mark.asyncio


async def _seed_agent_call(engine: object, user: User) -> tuple[uuid.UUID, uuid.UUID]:
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        agent = Agent(
            user_id=user.id,
            name="Lesson agent",
            pricing_tier="balanced",
            system_prompt="Be helpful and concise.",
            language="en-US",
        )
        session.add(agent)
        await session.flush()
        call = CallRecord(
            user_id=user_id_to_uuid(user.id),
            agent_id=agent.id,
            provider="test",
            provider_call_id=f"session-{uuid.uuid4()}",
            direction="outbound",
            status="completed",
            from_number="test",
            to_number="test",
            transcript="[User]: private transcript",
            ended_at=datetime.now(UTC),
        )
        session.add(call)
        await session.commit()
        return agent.id, call.id


async def test_lesson_crud_and_exports(
    authenticated_test_client: tuple[AsyncClient, User], test_engine: object
) -> None:
    client, user = authenticated_test_client
    agent_id, call_id = await _seed_agent_call(test_engine, user)
    path = f"/api/v1/agents/{agent_id}/lessons"

    created = await client.post(
        path,
        json={
            "source_call_id": str(call_id),
            "title": "  Greeting issue  ",
            "observation": ' =HYPERLINK("bad")',
            "recommended_action": "+change prompt",
        },
    )
    assert created.status_code == 201, created.text
    lesson = created.json()
    assert lesson["title"] == "Greeting issue"
    assert "transcript" not in lesson

    listed = await client.get(path)
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [lesson["id"]]

    updated = await client.patch(f"{path}/{lesson['id']}", json={"status": "archived"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "archived"

    csv_export = await client.get(f"{path}/export/csv")
    assert csv_export.status_code == 200
    assert "private transcript" not in csv_export.text
    assert "\t=HYPERLINK" in csv_export.text
    assert "\t+change prompt" in csv_export.text
    assert "attachment;" in csv_export.headers["content-disposition"]

    json_export = await client.get(f"{path}/export/json", params={"lesson_id": lesson["id"]})
    assert json_export.status_code == 200
    assert json_export.json()[0]["source_call_id"] == str(call_id)
    assert "private transcript" not in json_export.text

    removed = await client.delete(f"{path}/{lesson['id']}")
    assert removed.status_code == 204
    assert (await client.get(path)).json() == []


async def test_rejects_foreign_or_invalid_source_call(
    authenticated_test_client: tuple[AsyncClient, User], test_engine: object
) -> None:
    client, user = authenticated_test_client
    agent_id, _ = await _seed_agent_call(test_engine, user)
    payload = {
        "source_call_id": str(uuid.uuid4()),
        "title": "Title",
        "observation": "Observation",
        "recommended_action": "Action",
    }
    response = await client.post(f"/api/v1/agents/{agent_id}/lessons", json=payload)
    assert response.status_code == 400


async def test_cross_user_agent_is_denied(
    authenticated_test_client: tuple[AsyncClient, User], test_engine: object
) -> None:
    client, _ = authenticated_test_client
    session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        other = User(
            email="other@example.com",
            hashed_password="test_other_hash",  # noqa: S106
            is_active=True,
        )
        session.add(other)
        await session.flush()
        agent = Agent(
            user_id=other.id,
            name="Other agent",
            pricing_tier="balanced",
            system_prompt="A sufficiently long prompt.",
            language="en-US",
        )
        session.add(agent)
        await session.commit()
        agent_id = agent.id

    response = await client.get(f"/api/v1/agents/{agent_id}/lessons")
    assert response.status_code == 403


async def test_source_call_delete_cascades_lesson(
    authenticated_test_client: tuple[AsyncClient, User], test_engine: object
) -> None:
    client, user = authenticated_test_client
    agent_id, call_id = await _seed_agent_call(test_engine, user)
    created = await client.post(
        f"/api/v1/agents/{agent_id}/lessons",
        json={
            "source_call_id": str(call_id),
            "title": "Title",
            "observation": "Observation",
            "recommended_action": "Action",
        },
    )
    lesson_id = uuid.UUID(created.json()["id"])
    session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        await session.execute(delete(CallRecord).where(CallRecord.id == call_id))
        await session.commit()
        assert (
            await session.scalar(select(LessonLearned).where(LessonLearned.id == lesson_id)) is None
        )


async def test_validation_limits(
    authenticated_test_client: tuple[AsyncClient, User], test_engine: object
) -> None:
    client, user = authenticated_test_client
    agent_id, call_id = await _seed_agent_call(test_engine, user)
    response = await client.post(
        f"/api/v1/agents/{agent_id}/lessons",
        json={
            "source_call_id": str(call_id),
            "title": "x" * 201,
            "observation": "Observation",
            "recommended_action": "Action",
        },
    )
    assert response.status_code == 422
