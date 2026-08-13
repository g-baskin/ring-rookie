"""Add durable lessons linked to source call records.

Revision ID: 020_add_lessons
Revises: 019_add_prompt_target
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "020_add_lessons"
down_revision: str | None = "019_add_prompt_target"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the lessons learned table and access-path indexes."""
    op.create_table(
        "lessons_learned",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("agent_id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=True),
        sa.Column("source_call_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("observation", sa.Text(), nullable=False),
        sa.Column("recommended_action", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_call_id"], ["call_records.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lessons_learned_user_id", "lessons_learned", ["user_id"])
    op.create_index("ix_lessons_learned_agent_id", "lessons_learned", ["agent_id"])
    op.create_index("ix_lessons_learned_workspace_id", "lessons_learned", ["workspace_id"])
    op.create_index("ix_lessons_learned_source_call_id", "lessons_learned", ["source_call_id"])
    op.create_index("ix_lessons_learned_status", "lessons_learned", ["status"])
    op.create_index(
        "ix_lessons_owner_agent_created",
        "lessons_learned",
        ["user_id", "agent_id", "created_at"],
    )


def downgrade() -> None:
    """Drop the lessons learned table."""
    op.drop_index("ix_lessons_owner_agent_created", table_name="lessons_learned")
    op.drop_table("lessons_learned")
