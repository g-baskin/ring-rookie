"""Regression tests for authentication endpoints."""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.main import app


@pytest.mark.asyncio
async def test_register_accepts_json_payload_with_rate_limiter() -> None:
    """Ensure SlowAPI receives the HTTP request instead of the JSON model."""
    session = AsyncMock(spec=AsyncSession)
    query_result = MagicMock()
    query_result.scalar_one_or_none.return_value = None
    session.execute.return_value = query_result

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield session

    async def set_created_user_id(user: object) -> None:
        user.id = 1  # type: ignore[attr-defined]

    session.refresh.side_effect = set_created_user_id
    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)  # type: ignore[arg-type]
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "new-user@example.com",
                    "username": "New User",
                    "password": "TestPass123!",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "new-user@example.com",
        "username": "New User",
    }
    session.add.assert_called_once()
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once()
