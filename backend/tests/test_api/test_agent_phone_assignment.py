"""Focused tests for agent phone-number assignment and inbound routing."""

import uuid
from collections.abc import Awaitable, Callable

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.api.telephony import get_agent_by_phone_number
from app.models.agent import Agent
from app.models.user import User

PHONE_NUMBER = "+15551234567"


def make_agent(user_id: int, name: str, phone_number_id: str | None = None) -> Agent:
    return Agent(
        user_id=user_id,
        name=name,
        pricing_tier="balanced",
        system_prompt="You are a helpful test voice agent.",
        phone_number_id=phone_number_id,
    )


async def get_saved_agent(test_engine: AsyncEngine, agent_id: uuid.UUID) -> Agent:
    session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        result = await session.execute(select(Agent).where(Agent.id == agent_id))
        return result.scalar_one()


@pytest.mark.asyncio
async def test_assigns_phone_number_to_agent(
    authenticated_test_client: tuple[AsyncClient, User], test_engine: AsyncEngine
) -> None:
    client, user = authenticated_test_client
    session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        agent = make_agent(user.id, "Sales")
        session.add(agent)
        await session.commit()
        agent_id = agent.id

    response = await client.put(
        f"/api/v1/agents/{agent_id}", json={"phone_number_id": PHONE_NUMBER}
    )

    assert response.status_code == 200
    assert response.json()["phone_number_id"] == PHONE_NUMBER
    assert (await get_saved_agent(test_engine, agent_id)).phone_number_id == PHONE_NUMBER


@pytest.mark.asyncio
async def test_unassigns_phone_number_from_agent(
    authenticated_test_client: tuple[AsyncClient, User], test_engine: AsyncEngine
) -> None:
    client, user = authenticated_test_client
    session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        agent = make_agent(user.id, "Support", PHONE_NUMBER)
        session.add(agent)
        await session.commit()
        agent_id = agent.id

    response = await client.put(f"/api/v1/agents/{agent_id}", json={"phone_number_id": None})

    assert response.status_code == 200
    assert response.json()["phone_number_id"] is None
    assert (await get_saved_agent(test_engine, agent_id)).phone_number_id is None


@pytest.mark.asyncio
async def test_reassignment_removes_number_from_previous_agent(
    authenticated_test_client: tuple[AsyncClient, User], test_engine: AsyncEngine
) -> None:
    client, user = authenticated_test_client
    session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        previous_agent = make_agent(user.id, "Previous", PHONE_NUMBER.removeprefix("+"))
        next_agent = make_agent(user.id, "Next")
        session.add_all([previous_agent, next_agent])
        await session.commit()
        previous_agent_id = previous_agent.id
        next_agent_id = next_agent.id

    response = await client.put(
        f"/api/v1/agents/{next_agent_id}", json={"phone_number_id": PHONE_NUMBER}
    )

    assert response.status_code == 200
    assert (await get_saved_agent(test_engine, previous_agent_id)).phone_number_id is None
    assert (await get_saved_agent(test_engine, next_agent_id)).phone_number_id == PHONE_NUMBER


@pytest.mark.asyncio
async def test_cannot_assign_number_to_another_users_agent(
    authenticated_test_client: tuple[AsyncClient, User], test_engine: AsyncEngine
) -> None:
    client, _ = authenticated_test_client
    session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        other_user = User(
            email="other-owner@example.com",
            hashed_password="unused",  # noqa: S106 -- inert test value
        )
        session.add(other_user)
        await session.flush()
        other_agent = make_agent(other_user.id, "Private")
        session.add(other_agent)
        await session.commit()
        other_agent_id = other_agent.id

    response = await client.put(
        f"/api/v1/agents/{other_agent_id}", json={"phone_number_id": PHONE_NUMBER}
    )

    assert response.status_code == 404
    assert (await get_saved_agent(test_engine, other_agent_id)).phone_number_id is None


@pytest.mark.asyncio
@pytest.mark.parametrize("lookup_number", [PHONE_NUMBER, PHONE_NUMBER.removeprefix("+")])
async def test_inbound_lookup_normalizes_optional_plus_prefix(
    test_session: AsyncSession,
    create_test_user: Callable[..., Awaitable[User]],
    lookup_number: str,
) -> None:
    user = await create_test_user()
    agent = make_agent(user.id, "Inbound", PHONE_NUMBER)
    test_session.add(agent)
    await test_session.commit()

    found_agent = await get_agent_by_phone_number(lookup_number, test_session)

    assert found_agent is not None
    assert found_agent.id == agent.id
