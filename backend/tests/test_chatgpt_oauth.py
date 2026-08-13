"""Tests for ChatGPT/Codex OAuth security helpers."""

import base64
import json
import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse

import pytest
from cryptography.fernet import Fernet

from app.core.config import settings
from app.services import chatgpt_oauth


class FakeRedis:
    """Minimal Redis implementation for one-time OAuth state tests."""

    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    async def set(self, key: str, value: str, **_: object) -> bool:
        self.values[key] = value
        return True

    async def getdel(self, key: str) -> str | None:
        return self.values.pop(key, None)


@pytest.mark.asyncio
async def test_authorization_url_uses_pkce_and_single_use_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    redis = FakeRedis()

    async def fake_get_redis() -> FakeRedis:
        return redis

    async def fake_callback_relay() -> None:
        return None

    monkeypatch.setattr(chatgpt_oauth, "get_redis", fake_get_redis)
    monkeypatch.setattr(chatgpt_oauth, "ensure_callback_relay", fake_callback_relay)
    url = await chatgpt_oauth.create_authorization_url(42, "workspace-uuid")
    query = parse_qs(urlparse(url).query)

    assert query["response_type"] == ["code"]
    assert query["code_challenge_method"] == ["S256"]
    assert "offline_access" in query["scope"][0]
    assert query["redirect_uri"] == ["http://localhost:1455/auth/callback"]
    assert query["prompt"] == ["login"]
    assert query["originator"] == ["ggcoder"]
    assert "code_verifier" not in query

    state = await chatgpt_oauth.consume_state(query["state"][0])
    assert state.user_id == 42
    assert state.workspace_id == "workspace-uuid"
    with pytest.raises(chatgpt_oauth.ChatGPTOAuthError, match="already used"):
        await chatgpt_oauth.consume_state(query["state"][0])


def test_token_encryption_never_persists_plaintext(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "OAUTH_TOKEN_ENCRYPTION_KEY", Fernet.generate_key().decode())
    encrypted = chatgpt_oauth.encrypt_token("secret-access-token")

    assert "secret-access-token" not in encrypted
    assert chatgpt_oauth.decrypt_token(encrypted) == "secret-access-token"


def test_token_metadata_extracts_safe_account_claims() -> None:
    payload = {
        "email": "owner@example.com",
        "name": "Owner",
        "https://api.openai.com/auth": {
            "chatgpt_account_id": "account-123",
            "chatgpt_plan_type": "plus",
        },
    }
    encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()

    metadata = chatgpt_oauth.token_metadata(f"header.{encoded}.signature")

    assert metadata == {
        "email": "owner@example.com",
        "name": "Owner",
        "account_id": "account-123",
        "plan_type": "plus",
    }


def test_token_response_expiry_is_timezone_aware() -> None:
    tokens = chatgpt_oauth._parse_token_response(  # noqa: SLF001
        {"access_token": "token", "expires_in": 3600, "token_type": "Bearer"}
    )

    assert tokens.expires_at is not None
    assert tokens.expires_at.tzinfo == UTC
    assert tokens.expires_at > datetime.now(UTC)


class FakeScalarResult:
    def __init__(self, value: object) -> None:
        self.value = value

    def scalar_one_or_none(self) -> object:
        return self.value


class FakeSession:
    def __init__(self, connection: object) -> None:
        self.connection = connection
        self.commits = 0

    async def execute(self, _statement: object) -> FakeScalarResult:
        return FakeScalarResult(self.connection)

    async def commit(self) -> None:
        self.commits += 1


@pytest.mark.asyncio
async def test_get_access_token_returns_valid_workspace_oauth_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OAUTH_TOKEN_ENCRYPTION_KEY", Fernet.generate_key().decode())
    connection = SimpleNamespace(
        credentials={"access_token": chatgpt_oauth.encrypt_token("oauth-access-token")},
        expires_at=datetime.now(UTC) + timedelta(hours=1),
        refresh_token=None,
    )
    db = FakeSession(connection)

    token = await chatgpt_oauth.get_access_token(uuid.uuid4(), uuid.uuid4(), db)  # type: ignore[arg-type]

    assert token == "oauth-access-token"
    assert db.commits == 0


@pytest.mark.asyncio
async def test_get_access_token_refreshes_and_rotates_expiring_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "OAUTH_TOKEN_ENCRYPTION_KEY", Fernet.generate_key().decode())
    connection = SimpleNamespace(
        credentials={
            "access_token": chatgpt_oauth.encrypt_token("expired-access-token"),
            "id_token": chatgpt_oauth.encrypt_token("existing-id-token"),
        },
        expires_at=datetime.now(UTC),
        refresh_token=chatgpt_oauth.encrypt_token("refresh-token"),
        integration_metadata={},
        last_used_at=None,
        updated_at=None,
    )
    refreshed = chatgpt_oauth.OAuthTokens(
        access_token="new-access-token",  # noqa: S106 - synthetic credential
        refresh_token="new-refresh-token",  # noqa: S106 - synthetic credential
        id_token=None,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
        token_type="Bearer",  # noqa: S106 - OAuth token type
        scope="openid",
    )

    async def fake_refresh(refresh_token: str) -> chatgpt_oauth.OAuthTokens:
        assert refresh_token == "refresh-token"
        return refreshed

    monkeypatch.setattr(chatgpt_oauth, "refresh_tokens", fake_refresh)
    db = FakeSession(connection)

    token = await chatgpt_oauth.get_access_token(uuid.uuid4(), uuid.uuid4(), db)  # type: ignore[arg-type]

    assert token == "new-access-token"
    assert chatgpt_oauth.decrypt_token(connection.credentials["access_token"]) == token
    assert chatgpt_oauth.decrypt_token(connection.refresh_token) == "new-refresh-token"
    assert db.commits == 1
