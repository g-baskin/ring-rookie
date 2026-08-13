"""ChatGPT/Codex OAuth helpers with PKCE and encrypted token persistence."""

import base64
import hashlib
import json
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlencode

import httpx
from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings
from app.db.redis import get_redis
from app.services.oauth_callback_relay import ensure_callback_relay

CHATGPT_INTEGRATION_ID = "chatgpt-codex"
CHATGPT_INTEGRATION_NAME = "ChatGPT (Codex)"
STATE_TTL_SECONDS = 600
OAUTH_SCOPES = "openid profile email offline_access api.connectors.read api.connectors.invoke"


class ChatGPTOAuthError(Exception):
    """Safe error raised when the ChatGPT OAuth flow cannot complete."""


@dataclass(frozen=True)
class OAuthState:
    """Server-side data bound to a single OAuth authorization response."""

    user_id: int
    workspace_id: str | None
    code_verifier: str


@dataclass(frozen=True)
class OAuthTokens:
    """Validated token response returned by OpenAI Auth."""

    access_token: str
    refresh_token: str | None
    id_token: str | None
    expires_at: datetime | None
    token_type: str
    scope: str | None


def _state_key(state: str) -> str:
    return f"oauth:chatgpt:state:{state}"


def _fernet() -> Fernet:
    key = settings.OAUTH_TOKEN_ENCRYPTION_KEY
    if not key:
        raise ChatGPTOAuthError("ChatGPT OAuth token encryption is not configured")
    try:
        return Fernet(key.encode())
    except (TypeError, ValueError) as exc:
        raise ChatGPTOAuthError("ChatGPT OAuth token encryption key is invalid") from exc


def encrypt_token(token: str) -> str:
    """Encrypt a bearer token before database persistence."""
    return _fernet().encrypt(token.encode()).decode()


def decrypt_token(token: str) -> str:
    """Decrypt a persisted bearer token."""
    try:
        return _fernet().decrypt(token.encode()).decode()
    except InvalidToken as exc:
        raise ChatGPTOAuthError("Stored ChatGPT credentials could not be decrypted") from exc


def _generate_pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


async def create_authorization_url(user_id: int, workspace_id: str | None) -> str:
    """Create a PKCE authorization URL and persist one-time state in Redis."""
    await ensure_callback_relay()
    state = secrets.token_urlsafe(32)
    verifier, challenge = _generate_pkce()
    redis = await get_redis()
    await redis.set(
        _state_key(state),
        json.dumps(
            {
                "user_id": user_id,
                "workspace_id": workspace_id,
                "code_verifier": verifier,
            }
        ),
        ex=STATE_TTL_SECONDS,
        nx=True,
    )
    query = urlencode(
        {
            "response_type": "code",
            "client_id": settings.CHATGPT_OAUTH_CLIENT_ID,
            "redirect_uri": settings.CHATGPT_OAUTH_CALLBACK_URL,
            "scope": OAUTH_SCOPES,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "id_token_add_organizations": "true",
            "codex_cli_simplified_flow": "true",
            "state": state,
            "prompt": "login",
            "originator": "ggcoder",
        }
    )
    return f"{settings.CHATGPT_OAUTH_ISSUER.rstrip('/')}/oauth/authorize?{query}"


async def consume_state(state: str) -> OAuthState:
    """Atomically consume state so a callback cannot be replayed."""
    redis = await get_redis()
    key = _state_key(state)
    raw = await redis.getdel(key)
    if not raw:
        raise ChatGPTOAuthError("ChatGPT sign-in expired or was already used")
    try:
        data = json.loads(raw)
        return OAuthState(
            user_id=int(data["user_id"]),
            workspace_id=data.get("workspace_id"),
            code_verifier=str(data["code_verifier"]),
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ChatGPTOAuthError("ChatGPT sign-in state was invalid") from exc


def _decode_jwt_payload(token: str | None) -> dict[str, Any]:
    """Decode unverified claims only for account display metadata."""
    if not token:
        return {}
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload.encode())
        value = json.loads(decoded)
        return value if isinstance(value, dict) else {}
    except (IndexError, ValueError, json.JSONDecodeError):
        return {}


def token_metadata(id_token: str | None) -> dict[str, Any]:
    """Extract non-secret account metadata from an ID token."""
    claims = _decode_jwt_payload(id_token)
    auth_claims = claims.get("https://api.openai.com/auth", {})
    if not isinstance(auth_claims, dict):
        auth_claims = {}
    metadata: dict[str, Any] = {}
    for source, target in (
        ("email", "email"),
        ("name", "name"),
        ("chatgpt_account_id", "account_id"),
        ("chatgpt_plan_type", "plan_type"),
    ):
        value = claims.get(source) or auth_claims.get(source)
        if isinstance(value, str) and value:
            metadata[target] = value
    return metadata


def _parse_token_response(payload: dict[str, Any]) -> OAuthTokens:
    access_token = payload.get("access_token")
    if not isinstance(access_token, str) or not access_token:
        raise ChatGPTOAuthError("OpenAI did not return a ChatGPT access token")
    expires_at: datetime | None = None
    expires_in = payload.get("expires_in")
    if isinstance(expires_in, (int, float)) and expires_in > 0:
        expires_at = datetime.now(UTC) + timedelta(seconds=float(expires_in))
    return OAuthTokens(
        access_token=access_token,
        refresh_token=payload.get("refresh_token")
        if isinstance(payload.get("refresh_token"), str)
        else None,
        id_token=payload.get("id_token") if isinstance(payload.get("id_token"), str) else None,
        expires_at=expires_at,
        token_type=str(payload.get("token_type", "Bearer")),
        scope=payload.get("scope") if isinstance(payload.get("scope"), str) else None,
    )


async def _token_request(form: dict[str, str]) -> OAuthTokens:
    endpoint = f"{settings.CHATGPT_OAUTH_ISSUER.rstrip('/')}/oauth/token"
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                endpoint, data=form, headers={"Accept": "application/json"}
            )
    except httpx.RequestError as exc:
        raise ChatGPTOAuthError("OpenAI authentication is temporarily unavailable") from exc
    if not response.is_success:
        raise ChatGPTOAuthError("OpenAI rejected the ChatGPT authentication request")
    try:
        payload = response.json()
    except ValueError as exc:
        raise ChatGPTOAuthError("OpenAI returned an invalid authentication response") from exc
    if not isinstance(payload, dict):
        raise ChatGPTOAuthError("OpenAI returned an invalid authentication response")
    return _parse_token_response(payload)


async def exchange_code(code: str, code_verifier: str) -> OAuthTokens:
    """Exchange an authorization code using the matching PKCE verifier."""
    return await _token_request(
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.CHATGPT_OAUTH_CALLBACK_URL,
            "client_id": settings.CHATGPT_OAUTH_CLIENT_ID,
            "code_verifier": code_verifier,
        }
    )


async def refresh_tokens(refresh_token: str) -> OAuthTokens:
    """Refresh and rotate a ChatGPT OAuth token set."""
    return await _token_request(
        {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": settings.CHATGPT_OAUTH_CLIENT_ID,
        }
    )
