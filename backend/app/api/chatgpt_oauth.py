"""Persistent ChatGPT/Codex OAuth connection endpoints."""

import uuid
from datetime import UTC, datetime
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, user_id_to_uuid
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.models.user_integration import UserIntegration
from app.models.workspace import Workspace
from app.services.chatgpt_oauth import (
    CHATGPT_INTEGRATION_ID,
    CHATGPT_INTEGRATION_NAME,
    ChatGPTOAuthError,
    OAuthTokens,
    consume_state,
    create_authorization_url,
    decrypt_token,
    encrypt_token,
    exchange_code,
    refresh_tokens,
    token_metadata,
)

router = APIRouter(prefix="/api/v1/oauth/chatgpt", tags=["chatgpt-oauth"])


class ConnectResponse(BaseModel):
    """URL where the browser completes ChatGPT authorization."""

    authorization_url: str


class ConnectionStatus(BaseModel):
    """Safe, token-free ChatGPT connection status."""

    connected: bool
    workspace_id: str | None = None
    account_email: str | None = None
    account_name: str | None = None
    plan_type: str | None = None
    expires_at: datetime | None = None
    can_refresh: bool = False
    updated_at: datetime | None = None


class MessageResponse(BaseModel):
    """Mutation result."""

    message: str


def _redirect(result: str, detail: str | None = None) -> RedirectResponse:
    params = {"chatgpt_oauth": result}
    if detail:
        params["chatgpt_oauth_detail"] = detail
    return RedirectResponse(
        url=f"{settings.CHATGPT_OAUTH_FRONTEND_URL}?{urlencode(params)}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


async def _workspace_uuid(
    workspace_id: str | None, current_user_id: int, db: AsyncSession
) -> uuid.UUID | None:
    if workspace_id is None:
        return None
    try:
        parsed = uuid.UUID(workspace_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid workspace_id format") from exc
    result = await db.execute(
        select(Workspace.id).where(Workspace.id == parsed, Workspace.user_id == current_user_id)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return parsed


async def _connection(
    user_id: uuid.UUID, workspace_id: uuid.UUID | None, db: AsyncSession
) -> UserIntegration | None:
    workspace_condition = (
        UserIntegration.workspace_id == workspace_id
        if workspace_id is not None
        else UserIntegration.workspace_id.is_(None)
    )
    result = await db.execute(
        select(UserIntegration).where(
            and_(
                UserIntegration.user_id == user_id,
                UserIntegration.integration_id == CHATGPT_INTEGRATION_ID,
                workspace_condition,
            )
        )
    )
    return result.scalar_one_or_none()


def _status(connection: UserIntegration | None) -> ConnectionStatus:
    if connection is None:
        return ConnectionStatus(connected=False)
    metadata = connection.integration_metadata or {}
    return ConnectionStatus(
        connected=connection.is_active,
        workspace_id=str(connection.workspace_id) if connection.workspace_id else None,
        account_email=metadata.get("email"),
        account_name=metadata.get("name"),
        plan_type=metadata.get("plan_type"),
        expires_at=connection.expires_at,
        can_refresh=bool(connection.refresh_token),
        updated_at=connection.updated_at,
    )


def _apply_tokens(connection: UserIntegration, tokens: OAuthTokens) -> None:
    credentials = {
        "access_token": encrypt_token(tokens.access_token),
        "token_type": tokens.token_type,
    }
    if tokens.id_token:
        credentials["id_token"] = encrypt_token(tokens.id_token)
    connection.credentials = credentials
    connection.refresh_token = encrypt_token(tokens.refresh_token) if tokens.refresh_token else None
    connection.expires_at = tokens.expires_at
    connection.integration_metadata = {
        **(connection.integration_metadata or {}),
        **token_metadata(tokens.access_token),
        **token_metadata(tokens.id_token),
        "scope": tokens.scope,
        "auth_method": "oauth_pkce",
    }
    connection.is_active = True
    connection.updated_at = datetime.now(UTC)


@router.post("/connect", response_model=ConnectResponse)
async def connect_chatgpt(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    workspace_id: str | None = Query(None),
) -> ConnectResponse:
    """Start a one-time ChatGPT OAuth authorization-code flow."""
    workspace_uuid = await _workspace_uuid(workspace_id, current_user.id, db)
    try:
        authorization_url = await create_authorization_url(
            current_user.id,
            str(workspace_uuid) if workspace_uuid else None,
        )
    except ChatGPTOAuthError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return ConnectResponse(authorization_url=authorization_url)


@router.get("/callback")
async def chatgpt_callback(
    state: str | None = Query(None),
    code: str | None = Query(None),
    error: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    """Consume the OAuth callback and persist encrypted credentials."""
    if not state:
        return _redirect("error", "missing_state")
    try:
        oauth_state = await consume_state(state)
        if error:
            return _redirect("error", "authorization_denied")
        if not code:
            return _redirect("error", "missing_code")
        tokens = await exchange_code(code, oauth_state.code_verifier)
        user_result = await db.execute(
            select(User.id).where(User.id == oauth_state.user_id, User.is_active.is_(True))
        )
        user_is_active = user_result.scalar_one_or_none() is not None
        user_uuid = user_id_to_uuid(oauth_state.user_id)
        workspace_uuid = uuid.UUID(oauth_state.workspace_id) if oauth_state.workspace_id else None
        if workspace_uuid is not None:
            owner_result = await db.execute(
                select(Workspace.id).where(
                    Workspace.id == workspace_uuid,
                    Workspace.user_id == oauth_state.user_id,
                )
            )
            workspace_is_owned = owner_result.scalar_one_or_none() is not None
        else:
            workspace_is_owned = True
        if not user_is_active or not workspace_is_owned:
            return _redirect("error", "authentication_failed")
        connection = await _connection(user_uuid, workspace_uuid, db)
        if connection is None:
            connection = UserIntegration(
                user_id=user_uuid,
                workspace_id=workspace_uuid,
                integration_id=CHATGPT_INTEGRATION_ID,
                integration_name=CHATGPT_INTEGRATION_NAME,
                credentials={},
                integration_metadata={},
            )
            db.add(connection)
        _apply_tokens(connection, tokens)
        await db.commit()
    except (ChatGPTOAuthError, ValueError):
        await db.rollback()
        return _redirect("error", "authentication_failed")
    return _redirect("connected")


@router.get("/status", response_model=ConnectionStatus)
async def chatgpt_status(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    workspace_id: str | None = Query(None),
) -> ConnectionStatus:
    """Return the caller's selected-scope connection without secrets."""
    workspace_uuid = await _workspace_uuid(workspace_id, current_user.id, db)
    connection = await _connection(user_id_to_uuid(current_user.id), workspace_uuid, db)
    return _status(connection)


@router.post("/refresh", response_model=ConnectionStatus)
async def refresh_chatgpt_connection(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    workspace_id: str | None = Query(None),
) -> ConnectionStatus:
    """Refresh and rotate persistent ChatGPT credentials."""
    workspace_uuid = await _workspace_uuid(workspace_id, current_user.id, db)
    connection = await _connection(user_id_to_uuid(current_user.id), workspace_uuid, db)
    if connection is None or not connection.refresh_token:
        raise HTTPException(status_code=404, detail="Refreshable ChatGPT connection not found")
    try:
        tokens = await refresh_tokens(decrypt_token(connection.refresh_token))
        _apply_tokens(connection, tokens)
        await db.commit()
        await db.refresh(connection)
    except ChatGPTOAuthError as exc:
        await db.rollback()
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return _status(connection)


@router.delete("/connection", response_model=MessageResponse)
async def disconnect_chatgpt(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    workspace_id: str | None = Query(None),
) -> MessageResponse:
    """Delete the caller's selected-scope ChatGPT credentials."""
    workspace_uuid = await _workspace_uuid(workspace_id, current_user.id, db)
    connection = await _connection(user_id_to_uuid(current_user.id), workspace_uuid, db)
    if connection is None:
        raise HTTPException(status_code=404, detail="ChatGPT connection not found")
    await db.delete(connection)
    await db.commit()
    return MessageResponse(message="ChatGPT disconnected")
