"""Public text chat API for embed widgets.

This provides a text-based chat interface using GPT-4o-mini,
sharing the same agent configuration as voice widgets but at
a much lower cost (~$0.15/1M input, $0.60/1M output tokens).

Chat Champ adds streaming responses and persistent conversation storage.
"""

import hashlib
import json
import time
import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.embed import get_agent_by_public_id, validate_origin
from app.api.integrations import get_workspace_integrations
from app.api.settings import get_user_api_keys
from app.core.auth import user_id_to_uuid
from app.db.session import AsyncSessionLocal, get_db
from app.models.agent import Agent
from app.models.conversation import Conversation, Message
from app.models.workspace import AgentWorkspace, Workspace
from app.services.gpt_realtime import build_instructions_with_language
from app.services.knowledge_base import KnowledgeBaseService
from app.services.tools.registry import ToolRegistry
from app.services.usage import UsageService, UsageStatus

router = APIRouter(prefix="/api/public/chat", tags=["public-chat"])
logger = structlog.get_logger()

# GPT-4o-mini is the cheapest and best model for text chat
CHAT_MODEL = "gpt-4o-mini"


class ChatMessageRequest(BaseModel):
    """Request model for sending a chat message."""

    message: str
    conversation_history: list[dict[str, str]] = []


class StreamingChatRequest(BaseModel):
    """Request model for streaming chat messages."""

    message: str
    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Client session ID for conversation tracking",
    )
    conversation_id: str | None = Field(
        default=None,
        description="Existing conversation ID to continue",
    )


class ChatMessageResponse(BaseModel):
    """Response model for chat messages."""

    response: str
    conversation_history: list[dict[str, str]]


class StreamingChatResponse(BaseModel):
    """Response metadata for streaming chat (returned at end of stream)."""

    conversation_id: str
    message_id: str
    input_tokens: int
    output_tokens: int


async def _validate_agent_for_chat(
    public_id: str,
    origin: str | None,
    db: AsyncSession,
    log: Any,
) -> Agent:
    """Validate agent exists and is enabled for chat."""
    agent = await get_agent_by_public_id(public_id, db)
    if not agent:
        log.warning("agent_not_found")
        raise HTTPException(status_code=404, detail="Agent not found")

    if not agent.embed_enabled:
        log.warning("embed_disabled")
        raise HTTPException(status_code=403, detail="Chat is disabled for this agent")

    if not agent.is_active:
        log.warning("agent_inactive")
        raise HTTPException(status_code=403, detail="Agent is not active")

    if not validate_origin(origin, agent.allowed_domains):
        log.warning("origin_not_allowed", allowed=agent.allowed_domains)
        raise HTTPException(status_code=403, detail="Origin not allowed")

    return agent


async def _get_workspace_context(
    agent: Agent,
    db: AsyncSession,
    log: Any,
) -> tuple[AgentWorkspace, str, str]:
    """Get workspace, API key, and timezone for the agent."""
    workspace_result = await db.execute(
        select(AgentWorkspace).where(AgentWorkspace.agent_id == agent.id).limit(1)
    )
    agent_workspace = workspace_result.scalar_one_or_none()

    if not agent_workspace:
        log.warning("no_workspace_for_agent")
        raise HTTPException(status_code=500, detail="Agent not configured properly")

    user_uuid = user_id_to_uuid(agent.user_id)
    user_settings = await get_user_api_keys(
        user_uuid, db, workspace_id=agent_workspace.workspace_id
    )

    if not user_settings or not user_settings.openai_api_key:
        log.warning("workspace_missing_openai_key")
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key not configured for this workspace.",
        )

    ws_result = await db.execute(
        select(Workspace).where(Workspace.id == agent_workspace.workspace_id)
    )
    ws_obj = ws_result.scalar_one_or_none()
    workspace_timezone = (
        ws_obj.settings.get("timezone", "UTC") if ws_obj and ws_obj.settings else "UTC"
    )

    return agent_workspace, user_settings.openai_api_key, workspace_timezone


def _build_chat_system_prompt(agent: Agent, workspace_timezone: str) -> str:
    """Build system prompt for text chat with anti-hallucination guardrails."""
    system_prompt = agent.system_prompt or "You are a helpful assistant."
    chat_system_prompt = build_instructions_with_language(
        system_prompt, agent.language, timezone=workspace_timezone
    )

    # Adapt voice prompts for text chat
    chat_system_prompt = chat_system_prompt.replace(
        "Keep responses concise - this is voice, not text",
        "You are responding via text chat. You can be slightly more detailed than voice.",
    )

    # Add critical rules for text chat formatting
    chat_system_prompt += """

## CRITICAL RULES FOR TEXT CHAT
- This is TEXT CHAT, not a phone call - use proper written formatting
- Write emails as: user@example.com (NOT "user at example dot com")
- Write URLs as: https://example.com (NOT "example dot com")
- Write phone numbers as: (555) 123-4567 (NOT "five five five...")
- Use symbols and punctuation normally: @, #, $, %, &, etc.
- NEVER spell out special characters - this is text, not voice
- NEVER make up or assume user information not explicitly provided"""

    return chat_system_prompt


async def _get_tools_for_agent(
    agent: Agent,
    agent_workspace: AgentWorkspace,
    db: AsyncSession,
) -> tuple[list[dict[str, Any]] | None, ToolRegistry | None]:
    """Get tool definitions for the agent if tools are enabled."""
    if not agent.enabled_tools and not agent.enabled_tool_ids:
        return None, None

    user_uuid = user_id_to_uuid(agent.user_id)
    integrations = await get_workspace_integrations(user_uuid, agent_workspace.workspace_id, db)

    tool_registry = ToolRegistry(
        db=db,
        user_id=agent.user_id,
        integrations=integrations,
        workspace_id=agent_workspace.workspace_id,
    )

    tool_defs = tool_registry.get_all_tool_definitions(
        agent.enabled_tools or [], agent.enabled_tool_ids
    )

    if not tool_defs:
        await tool_registry.close()
        return None, None

    tools = [
        {
            "type": "function",
            "function": {
                "name": t.get("name"),
                "description": t.get("description", ""),
                "parameters": t.get("parameters", {}),
            },
        }
        for t in tool_defs
        if t.get("name")
    ]

    return tools, tool_registry


async def _handle_tool_calls(
    assistant_message: Any,
    tool_registry: ToolRegistry,
    messages: list[dict[str, Any]],
    log: Any,
) -> list[dict[str, Any]]:
    """Execute tool calls and return results."""
    tool_results = []
    for tool_call in assistant_message.tool_calls:
        try:
            args = json.loads(tool_call.function.arguments)
            result = await tool_registry.execute_tool(tool_call.function.name, args)
            tool_results.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": json.dumps(result),
                }
            )
        except Exception as e:
            log.exception("tool_execution_error", tool=tool_call.function.name)
            tool_results.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": json.dumps({"error": str(e)}),
                }
            )

    messages.append(assistant_message.model_dump())
    messages.extend(tool_results)
    return messages


@router.post("/{public_id}/message", response_model=ChatMessageResponse)
async def send_chat_message(
    public_id: str,
    request: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
    origin: str | None = Header(None),
) -> ChatMessageResponse:
    """Send a text message and get an AI response.

    Uses GPT-4o-mini for cost-effective text chat while sharing
    the same agent configuration (system prompt, personality) as voice.
    """
    log = logger.bind(
        endpoint="chat_message",
        public_id=public_id,
        origin=origin,
        message_length=len(request.message),
    )

    agent = await _validate_agent_for_chat(public_id, origin, db, log)
    agent_workspace, api_key, workspace_timezone = await _get_workspace_context(agent, db, log)

    chat_system_prompt = _build_chat_system_prompt(agent, workspace_timezone)

    messages: list[dict[str, Any]] = [{"role": "system", "content": chat_system_prompt}]
    for msg in request.conversation_history:
        if msg.get("role") in ("user", "assistant") and msg.get("content"):
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": request.message})

    tools, tool_registry = await _get_tools_for_agent(agent, agent_workspace, db)

    log.info("sending_chat_request", model=CHAT_MODEL, message_count=len(messages))

    try:
        client = AsyncOpenAI(api_key=api_key)
        completion_kwargs: dict[str, Any] = {
            "model": CHAT_MODEL,
            "messages": messages,
            "temperature": agent.temperature if agent.temperature else 0.7,
            "max_tokens": 1024,
        }
        if tools:
            completion_kwargs["tools"] = tools
            completion_kwargs["tool_choice"] = "auto"

        response = await client.chat.completions.create(**completion_kwargs)
        assistant_message = response.choices[0].message

        if assistant_message.tool_calls and tool_registry:
            messages = await _handle_tool_calls(assistant_message, tool_registry, messages, log)
            response = await client.chat.completions.create(
                model=CHAT_MODEL,
                messages=messages,  # type: ignore[arg-type]
                temperature=agent.temperature if agent.temperature else 0.7,
                max_tokens=1024,
            )
            assistant_message = response.choices[0].message

        response_text = assistant_message.content or "I'm sorry, I couldn't generate a response."

        log.info(
            "chat_response_generated",
            response_length=len(response_text),
            tokens_used=response.usage.total_tokens if response.usage else 0,
        )

        updated_history = list(request.conversation_history)
        updated_history.append({"role": "user", "content": request.message})
        updated_history.append({"role": "assistant", "content": response_text})

        return ChatMessageResponse(
            response=response_text,
            conversation_history=updated_history,
        )

    except Exception as e:
        log.exception("chat_api_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {e!s}") from e
    finally:
        if tool_registry:
            await tool_registry.close()


@router.get("/{public_id}/config")
async def get_chat_config(
    public_id: str,
    db: AsyncSession = Depends(get_db),
    origin: str | None = Header(None),
) -> dict[str, Any]:
    """Get agent configuration for chat widget initialization."""
    log = logger.bind(endpoint="chat_config", public_id=public_id, origin=origin)

    agent = await _validate_agent_for_chat(public_id, origin, db, log)
    embed_settings = agent.embed_settings or {}

    log.info("chat_config_returned")

    return {
        "public_id": public_id,
        "name": agent.name,
        "greeting_message": embed_settings.get("greeting_message", "Hi! How can I help you today?"),
        "language": agent.language,
    }


# =============================================================================
# Chat Champ Streaming API (SSE)
# =============================================================================


def _generate_visitor_hash(request: Request) -> str:
    """Generate a hash for visitor tracking (privacy-preserving)."""
    user_agent = request.headers.get("user-agent", "")
    # Hash IP + User-Agent for privacy
    data = f"{user_agent}:{datetime.now(UTC).date()}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


async def _get_or_create_conversation(
    db: AsyncSession,
    agent_id: uuid.UUID,
    session_id: str,
    conversation_id: str | None,
    visitor_metadata: dict[str, Any],
) -> Conversation:
    """Get existing conversation or create a new one."""
    if conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == uuid.UUID(conversation_id),
                Conversation.agent_id == agent_id,
            )
        )
        conversation = result.scalar_one_or_none()
        if conversation:
            return conversation

    # Create new conversation
    conversation = Conversation(
        agent_id=agent_id,
        session_id=session_id,
        visitor_metadata=visitor_metadata,
        status="active",
        started_at=datetime.now(UTC),
    )
    db.add(conversation)
    await db.flush()
    return conversation


async def _save_message(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    role: str,
    content: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    model: str | None = None,
    extra_data: dict[str, Any] | None = None,
) -> Message:
    """Save a message to the conversation."""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        model=model,
        extra_data=extra_data or {},
    )
    db.add(message)
    await db.flush()
    return message


async def _update_conversation_stats(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    message_count_delta: int,
    token_delta: int,
) -> None:
    """Update conversation statistics."""
    await db.execute(
        update(Conversation)
        .where(Conversation.id == conversation_id)
        .values(
            message_count=Conversation.message_count + message_count_delta,
            total_tokens=Conversation.total_tokens + token_delta,
            last_message_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    )


async def _load_conversation_history(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    max_messages: int = 20,
) -> list[dict[str, str]]:
    """Load recent messages from a conversation."""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(max_messages)
    )
    messages = result.scalars().all()
    # Reverse to get chronological order
    return [
        {"role": msg.role, "content": msg.content}
        for msg in reversed(messages)
        if msg.role in ("user", "assistant")
    ]


class _StreamContext:
    """Context object for streaming chat."""

    agent: Agent
    api_key: str
    timezone: str
    conversation: Conversation
    usage_status: UsageStatus
    is_new_conversation: bool


async def _validate_and_setup_stream(
    db: AsyncSession,
    public_id: str,
    origin: str | None,
    request_data: StreamingChatRequest,
    visitor_hash: str,
    user_agent: str,
) -> _StreamContext | str:
    """Validate agent and set up streaming context. Returns error message string if failed."""
    agent = await get_agent_by_public_id(public_id, db)

    # Validate agent exists and is accessible
    if not agent or not agent.embed_enabled or not agent.is_active:
        return "Agent not found" if not agent else "Agent not available"
    if not validate_origin(origin, agent.allowed_domains):
        return "Origin not allowed"

    # Get workspace context
    workspace_result = await db.execute(
        select(AgentWorkspace).where(AgentWorkspace.agent_id == agent.id).limit(1)
    )
    agent_workspace = workspace_result.scalar_one_or_none()
    if not agent_workspace:
        return "Agent not configured"

    user_uuid = user_id_to_uuid(agent.user_id)
    user_settings = await get_user_api_keys(
        user_uuid, db, workspace_id=agent_workspace.workspace_id
    )
    if not user_settings or not user_settings.openai_api_key:
        return "API key not configured"

    # Get workspace timezone
    ws_result = await db.execute(
        select(Workspace).where(Workspace.id == agent_workspace.workspace_id)
    )
    ws_obj = ws_result.scalar_one_or_none()
    timezone = ws_obj.settings.get("timezone", "UTC") if ws_obj and ws_obj.settings else "UTC"

    # Check usage limits before allowing message
    usage_service = UsageService(db)
    usage_status = await usage_service.check_usage_limit(agent.id)
    if not usage_status.is_allowed:
        return f"Rate limit exceeded. Resets at {usage_status.reset_at.isoformat()}"

    # Get or create conversation
    is_new_conversation = request_data.conversation_id is None
    conversation = await _get_or_create_conversation(
        db=db,
        agent_id=agent.id,
        session_id=request_data.session_id,
        conversation_id=request_data.conversation_id,
        visitor_metadata={
            "visitor_hash": visitor_hash,
            "user_agent": user_agent[:200],
            "origin": origin,
        },
    )
    # Check if we actually created a new conversation (vs found existing)
    is_new_conversation = is_new_conversation or (conversation.message_count == 0)

    ctx = _StreamContext()
    ctx.agent = agent
    ctx.api_key = user_settings.openai_api_key
    ctx.timezone = timezone
    ctx.conversation = conversation
    ctx.usage_status = usage_status
    ctx.is_new_conversation = is_new_conversation
    return ctx


async def _stream_chat_response(
    public_id: str,
    request_data: StreamingChatRequest,
    origin: str | None,
    visitor_hash: str,
    user_agent: str,
) -> AsyncGenerator[str, None]:
    """Generate streaming chat response with SSE format."""
    start_time = time.time()
    log = logger.bind(
        endpoint="stream_chat", public_id=public_id, session_id=request_data.session_id
    )

    async with AsyncSessionLocal() as db:
        try:
            # Validate and set up context
            ctx = await _validate_and_setup_stream(
                db, public_id, origin, request_data, visitor_hash, user_agent
            )
            if isinstance(ctx, str):
                yield f"data: {json.dumps({'error': ctx})}\n\n"
                return

            # Load conversation history and build messages
            history = await _load_conversation_history(db, ctx.conversation.id)
            chat_system_prompt = _build_chat_system_prompt(ctx.agent, ctx.timezone)

            # Add RAG context from knowledge bases if available (optional feature)
            # Uses savepoint so failures don't abort the main transaction
            try:
                async with db.begin_nested():
                    kb_service = KnowledgeBaseService(db, ctx.api_key)
                    rag_context = await kb_service.get_rag_context_for_query(
                        agent_id=ctx.agent.id,
                        query=request_data.message,
                    )
                    if rag_context:
                        chat_system_prompt += "\n" + rag_context
                        log.info("rag_context_added", context_length=len(rag_context))
            except Exception as e:
                # RAG is optional - log and continue without it
                log.debug("rag_context_skipped", reason=str(e))

            messages: list[dict[str, Any]] = [{"role": "system", "content": chat_system_prompt}]
            messages.extend(history)
            messages.append({"role": "user", "content": request_data.message})

            # Save user message and send start event
            await _save_message(
                db=db,
                conversation_id=ctx.conversation.id,
                role="user",
                content=request_data.message,
            )
            yield f"data: {json.dumps({'type': 'start', 'conversation_id': str(ctx.conversation.id)})}\n\n"

            # Stream from OpenAI
            client = AsyncOpenAI(api_key=ctx.api_key)
            log.info("streaming_chat_request", model=CHAT_MODEL, message_count=len(messages))

            stream = await client.chat.completions.create(  # type: ignore[call-overload]
                model=CHAT_MODEL,
                messages=messages,
                temperature=ctx.agent.temperature or 0.7,
                max_tokens=1024,
                stream=True,
                stream_options={"include_usage": True},
            )

            full_response, input_tokens, output_tokens = "", 0, 0
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    full_response += token
                    yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                if chunk.usage:
                    input_tokens, output_tokens = (
                        chunk.usage.prompt_tokens,
                        chunk.usage.completion_tokens,
                    )

            # Save assistant message and update stats
            latency_ms = int((time.time() - start_time) * 1000)
            assistant_msg = await _save_message(
                db=db,
                conversation_id=ctx.conversation.id,
                role="assistant",
                content=full_response,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=CHAT_MODEL,
                extra_data={"latency_ms": latency_ms},
            )
            await _update_conversation_stats(
                db, ctx.conversation.id, 2, input_tokens + output_tokens
            )

            # Record usage for billing
            usage_service = UsageService(db)
            await usage_service.record_message(
                agent_id=ctx.agent.id,
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens,
                is_new_conversation=ctx.is_new_conversation,
            )

            await db.commit()

            yield f"data: {json.dumps({'type': 'done', 'conversation_id': str(ctx.conversation.id), 'message_id': str(assistant_msg.id), 'input_tokens': input_tokens, 'output_tokens': output_tokens})}\n\n"
            log.info(
                "streaming_complete",
                response_length=len(full_response),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
            )

        except Exception as e:
            log.exception("streaming_chat_error", error=str(e))
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            await db.rollback()


@router.post("/{public_id}/stream")
async def stream_chat_message(
    public_id: str,
    request_data: StreamingChatRequest,
    request: Request,
    origin: str | None = Header(None),
) -> StreamingResponse:
    """Stream a chat response using Server-Sent Events.

    Returns tokens as they are generated for real-time display.
    Persists conversation and messages to database for history.

    SSE Event Types:
    - start: {type: "start", conversation_id: "..."}
    - token: {type: "token", content: "..."}
    - done: {type: "done", conversation_id, message_id, input_tokens, output_tokens}
    - error: {type: "error", error: "..."}
    """
    visitor_hash = _generate_visitor_hash(request)
    user_agent = request.headers.get("user-agent", "")

    return StreamingResponse(
        _stream_chat_response(
            public_id=public_id,
            request_data=request_data,
            origin=origin,
            visitor_hash=visitor_hash,
            user_agent=user_agent,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get("/{public_id}/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    public_id: str,
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    origin: str | None = Header(None),
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Get messages from a conversation for history display."""
    log = logger.bind(
        endpoint="get_messages",
        public_id=public_id,
        conversation_id=conversation_id,
    )

    agent = await _validate_agent_for_chat(public_id, origin, db, log)

    # Verify conversation belongs to this agent
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == uuid.UUID(conversation_id),
            Conversation.agent_id == agent.id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get messages with pagination
    messages_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
        .offset(offset)
        .limit(limit)
    )
    messages = messages_result.scalars().all()

    return {
        "conversation_id": str(conversation.id),
        "messages": [
            {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ],
        "total_messages": conversation.message_count,
        "has_more": offset + len(messages) < conversation.message_count,
    }
