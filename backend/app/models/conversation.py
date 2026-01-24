"""Chat conversation and message models for Chat Champ.

Provides persistent storage for text chat conversations,
enabling conversation history, analytics, and usage tracking.
"""

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.agent import Agent


class Conversation(Base):
    """A chat conversation session.

    Tracks a single chat session between a visitor and an agent.
    Can span multiple messages over time.
    """

    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Agent handling this conversation",
    )

    # Session tracking (anonymous visitors identified by session)
    session_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="Client-generated session ID for visitor tracking",
    )

    # Conversation metadata
    visitor_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Visitor info: user_agent, ip_hash, referrer, etc.",
    )

    # Status tracking
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        index=True,
        comment="Conversation status: active, ended, archived",
    )

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        comment="When conversation started",
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When conversation ended (if ended)",
    )
    last_message_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp of most recent message",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Statistics (denormalized for quick access)
    message_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total messages in conversation",
    )
    total_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total tokens used in conversation",
    )

    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", lazy="selectin")
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )

    def __repr__(self) -> str:
        return (
            f"<Conversation(id={self.id}, agent_id={self.agent_id}, messages={self.message_count})>"
        )


class Message(Base):
    """A single message in a conversation.

    Stores the content, role, and token usage for billing.
    """

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Parent conversation",
    )

    # Message content
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Message role: user, assistant, system, tool",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Message content",
    )

    # Token usage for billing
    input_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Input tokens used for this message",
    )
    output_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Output tokens generated for this message",
    )

    # Model and extra data
    model: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Model used for this message (e.g., gpt-4o-mini)",
    )
    extra_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Additional metadata: tool_calls, latency_ms, etc.",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")

    def __repr__(self) -> str:
        preview_length = 50
        if len(self.content) > preview_length:
            content_preview = self.content[:preview_length] + "..."
        else:
            content_preview = self.content
        return f"<Message(id={self.id}, role={self.role}, content='{content_preview}')>"
