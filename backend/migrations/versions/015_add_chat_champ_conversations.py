"""Add conversations and messages tables for Chat Champ.

Revision ID: 015_add_chat_champ_conversations
Revises: fca9f1b81524
Create Date: 2025-01-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "015_add_chat_champ_conversations"
down_revision: str | None = "fca9f1b81524"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create conversations and messages tables."""
    # Create conversations table
    op.create_table(
        "conversations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "agent_id",
            sa.Uuid(),
            nullable=False,
            comment="Agent handling this conversation",
        ),
        sa.Column(
            "session_id",
            sa.String(64),
            nullable=False,
            comment="Client-generated session ID for visitor tracking",
        ),
        sa.Column(
            "visitor_metadata",
            JSONB(),
            nullable=False,
            server_default="{}",
            comment="Visitor info: user_agent, ip_hash, referrer, etc.",
        ),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="active",
            comment="Conversation status: active, ended, archived",
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
            comment="When conversation started",
        ),
        sa.Column(
            "ended_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="When conversation ended (if ended)",
        ),
        sa.Column(
            "last_message_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Timestamp of most recent message",
        ),
        sa.Column(
            "message_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Total messages in conversation",
        ),
        sa.Column(
            "total_tokens",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Total tokens used in conversation",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            ondelete="CASCADE",
        ),
    )

    # Create indexes for conversations
    op.create_index("ix_conversations_agent_id", "conversations", ["agent_id"])
    op.create_index("ix_conversations_session_id", "conversations", ["session_id"])
    op.create_index("ix_conversations_status", "conversations", ["status"])
    op.create_index("ix_conversations_last_message_at", "conversations", ["last_message_at"])
    op.create_index(
        "ix_conversations_agent_started_at",
        "conversations",
        ["agent_id", "started_at"],
    )

    # Create messages table
    op.create_table(
        "messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "conversation_id",
            sa.Uuid(),
            nullable=False,
            comment="Parent conversation",
        ),
        sa.Column(
            "role",
            sa.String(20),
            nullable=False,
            comment="Message role: user, assistant, system, tool",
        ),
        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
            comment="Message content",
        ),
        sa.Column(
            "input_tokens",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Input tokens used for this message",
        ),
        sa.Column(
            "output_tokens",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Output tokens generated for this message",
        ),
        sa.Column(
            "model",
            sa.String(50),
            nullable=True,
            comment="Model used for this message (e.g., gpt-4o-mini)",
        ),
        sa.Column(
            "extra_data",
            JSONB(),
            nullable=False,
            server_default="{}",
            comment="Additional metadata: tool_calls, latency_ms, etc.",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            ondelete="CASCADE",
        ),
    )

    # Create indexes for messages
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])
    op.create_index("ix_messages_created_at", "messages", ["created_at"])
    op.create_index(
        "ix_messages_conversation_created",
        "messages",
        ["conversation_id", "created_at"],
    )


def downgrade() -> None:
    """Drop conversations and messages tables."""
    # Drop messages indexes and table
    op.drop_index("ix_messages_conversation_created", "messages")
    op.drop_index("ix_messages_created_at", "messages")
    op.drop_index("ix_messages_conversation_id", "messages")
    op.drop_table("messages")

    # Drop conversations indexes and table
    op.drop_index("ix_conversations_agent_started_at", "conversations")
    op.drop_index("ix_conversations_last_message_at", "conversations")
    op.drop_index("ix_conversations_status", "conversations")
    op.drop_index("ix_conversations_session_id", "conversations")
    op.drop_index("ix_conversations_agent_id", "conversations")
    op.drop_table("conversations")
