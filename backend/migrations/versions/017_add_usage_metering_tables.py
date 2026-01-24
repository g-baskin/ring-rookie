"""Add usage metering tables for Chat Champ billing.

Revision ID: 017_add_usage_metering_tables
Revises: 015_add_chat_champ_conversations
Create Date: 2025-01-23

Tables:
- usage_records: Daily usage tracking per agent
- agent_billing_configs: Billing tier and limits per agent

Note: Knowledge base tables (016) skipped - requires pgvector extension.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "017_add_usage_metering_tables"
down_revision: str | None = "015_add_chat_champ_conversations"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create usage_records table
    op.create_table(
        "usage_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("agent_id", sa.Uuid(), nullable=False),
        sa.Column("usage_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("message_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("conversation_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completion_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("embedding_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("knowledge_base_bytes", sa.Integer(), nullable=False, server_default="0"),
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
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for usage_records
    op.create_index(
        "ix_usage_records_agent_id",
        "usage_records",
        ["agent_id"],
    )
    op.create_index(
        "ix_usage_records_date",
        "usage_records",
        ["usage_date"],
    )
    op.create_index(
        "ix_usage_records_agent_date",
        "usage_records",
        ["agent_id", "usage_date"],
        unique=True,
    )

    # Create agent_billing_configs table
    op.create_table(
        "agent_billing_configs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("agent_id", sa.Uuid(), nullable=False),
        sa.Column("tier", sa.String(20), nullable=False, server_default="free"),
        sa.Column("custom_message_limit", sa.Integer(), nullable=True),
        sa.Column("custom_storage_limit_mb", sa.Integer(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for agent_billing_configs
    op.create_index(
        "ix_agent_billing_configs_agent_id",
        "agent_billing_configs",
        ["agent_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_agent_billing_configs_agent_id", table_name="agent_billing_configs")
    op.drop_table("agent_billing_configs")

    op.drop_index("ix_usage_records_agent_date", table_name="usage_records")
    op.drop_index("ix_usage_records_date", table_name="usage_records")
    op.drop_index("ix_usage_records_agent_id", table_name="usage_records")
    op.drop_table("usage_records")
