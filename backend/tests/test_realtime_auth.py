"""Tests for workspace OpenAI Authentication used by Realtime endpoints."""

import uuid
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, cast

import httpx
import pytest
import structlog
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import realtime
from app.services.chatgpt_oauth import ChatGPTOAuthError

if TYPE_CHECKING:
    from app.models.user import User


@pytest.mark.asyncio
async def test_realtime_auth_falls_back_to_workspace_oauth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_uuid = uuid.uuid4()
    workspace_uuid = uuid.uuid4()
    db = cast("AsyncSession", object())

    async def no_api_key(*_args: object, **_kwargs: object) -> None:
        return None

    async def oauth_token(
        requested_user: uuid.UUID,
        requested_workspace: uuid.UUID | None,
        requested_db: AsyncSession,
    ) -> str:
        assert requested_user == user_uuid
        assert requested_workspace == workspace_uuid
        assert requested_db is db
        return "workspace-oauth-token"

    monkeypatch.setattr(realtime, "get_user_api_keys", no_api_key)
    monkeypatch.setattr(realtime, "get_access_token", oauth_token)

    token = await realtime.get_openai_auth_token_for_workspace(
        user_uuid, workspace_uuid, db, structlog.get_logger()
    )

    assert token == "workspace-oauth-token"


@pytest.mark.asyncio
async def test_realtime_auth_reports_missing_openai_authentication(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def no_api_key(*_args: object, **_kwargs: object) -> None:
        return None

    async def no_oauth(*_args: object, **_kwargs: object) -> str:
        raise ChatGPTOAuthError("not connected")

    monkeypatch.setattr(realtime, "get_user_api_keys", no_api_key)
    monkeypatch.setattr(realtime, "get_access_token", no_oauth)

    with pytest.raises(HTTPException) as exc_info:
        await realtime.get_openai_auth_token_for_workspace(
            uuid.uuid4(),
            uuid.uuid4(),
            cast("AsyncSession", object()),
            structlog.get_logger(),
        )

    assert exc_info.value.status_code == 400
    assert "OpenAI Authentication is not connected" in exc_info.value.detail


@pytest.mark.asyncio
async def test_ephemeral_token_uses_ga_client_secrets_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    agent_id = uuid.uuid4()
    workspace_id = uuid.uuid4()
    agent = SimpleNamespace(
        id=agent_id,
        is_active=True,
        pricing_tier="premium",
        voice="marin",
        enabled_tools=[],
        enabled_tool_ids=[],
        system_prompt="Be helpful.",
        language="en-US",
        name="Test Agent",
        initial_greeting=None,
    )

    class FakeResult:
        def scalar_one_or_none(self) -> SimpleNamespace:
            return agent

    class FakeSession:
        async def execute(self, _statement: object) -> FakeResult:
            return FakeResult()

    request: dict[str, Any] = {}

    class FakeAsyncClient:
        async def __aenter__(self) -> "FakeAsyncClient":
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

        async def post(self, url: str, **kwargs: Any) -> httpx.Response:
            request.update(url=url, **kwargs)
            return httpx.Response(
                200,
                request=httpx.Request("POST", url),
                json={
                    "value": "ek_test_client_secret",
                    "expires_at": 1_800_000_000,
                    "session": {"model": "gpt-realtime-2025-08-28"},
                },
            )

    class FakeToolRegistry:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            pass

        def get_all_tool_definitions(self, *_args: object) -> list[dict[str, Any]]:
            return []

    async def auth_token(*_args: object, **_kwargs: object) -> str:
        return "workspace-oauth-token"

    async def integrations(*_args: object, **_kwargs: object) -> dict[str, dict[str, Any]]:
        return {}

    monkeypatch.setattr(realtime, "get_openai_auth_token_for_workspace", auth_token)
    monkeypatch.setattr(realtime, "get_workspace_integrations", integrations)
    monkeypatch.setattr(realtime, "ToolRegistry", FakeToolRegistry)
    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)

    response = await realtime.get_ephemeral_token(
        str(agent_id),
        cast("User", SimpleNamespace(id=7)),
        cast("AsyncSession", FakeSession()),
        str(workspace_id),
    )

    assert request["url"] == "https://api.openai.com/v1/realtime/client_secrets"
    assert request["json"] == {
        "session": {
            "type": "realtime",
            "model": "gpt-realtime-2025-08-28",
            "audio": {"output": {"voice": "marin"}},
        }
    }
    assert response["client_secret"] == {
        "value": "ek_test_client_secret",
        "expires_at": 1_800_000_000,
    }


@pytest.mark.asyncio
async def test_save_transcript_authorizes_selected_workspace() -> None:
    agent_id = uuid.uuid4()
    workspace_id = uuid.uuid4()
    agent = SimpleNamespace(id=agent_id, user_id=999)
    agent_workspace = SimpleNamespace(agent_id=agent_id, workspace_id=workspace_id)

    class FakeResult:
        def __init__(self, value: object) -> None:
            self.value = value

        def scalar_one_or_none(self) -> object:
            return self.value

    class FakeSession:
        def __init__(self) -> None:
            self.results = iter((agent, agent_workspace))

        async def execute(self, _statement: object) -> FakeResult:
            return FakeResult(next(self.results))

    response = await realtime.save_transcript(
        str(agent_id),
        realtime.SaveTranscriptRequest(
            session_id="test-session",
            transcript=" ",
            duration_seconds=0,
        ),
        cast("User", SimpleNamespace(id=7)),
        cast("AsyncSession", FakeSession()),
        str(workspace_id),
    )

    assert response == {"success": True, "message": "Empty transcript skipped"}


@pytest.mark.asyncio
async def test_save_transcript_authorizes_admin_agent_owner() -> None:
    agent_id = uuid.uuid4()
    agent = SimpleNamespace(id=agent_id, user_id=7)

    class FakeResult:
        def scalar_one_or_none(self) -> SimpleNamespace:
            return agent

    class FakeSession:
        async def execute(self, _statement: object) -> FakeResult:
            return FakeResult()

    response = await realtime.save_transcript(
        str(agent_id),
        realtime.SaveTranscriptRequest(
            session_id="test-session",
            transcript=" ",
            duration_seconds=0,
        ),
        cast("User", SimpleNamespace(id=7)),
        cast("AsyncSession", FakeSession()),
    )

    assert response == {"success": True, "message": "Empty transcript skipped"}
