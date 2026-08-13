"""add chatgpt oauth integration uniqueness

Revision ID: 1df9973696e0
Revises: ca97ba39b920
Create Date: 2026-08-13 00:13:18.778397

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "1df9973696e0"
down_revision: Union[str, Sequence[str], None] = "ca97ba39b920"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Allow one ChatGPT OAuth connection per user and selected scope."""
    op.create_index(
        "uq_user_integrations_chatgpt_user_scope",
        "user_integrations",
        ["user_id", "integration_id"],
        unique=True,
        postgresql_where=sa.text("workspace_id IS NULL AND integration_id = 'chatgpt-codex'"),
    )
    op.create_index(
        "uq_user_integrations_chatgpt_workspace_scope",
        "user_integrations",
        ["user_id", "workspace_id", "integration_id"],
        unique=True,
        postgresql_where=sa.text("workspace_id IS NOT NULL AND integration_id = 'chatgpt-codex'"),
    )


def downgrade() -> None:
    """Remove ChatGPT OAuth scoped uniqueness."""
    op.drop_index("uq_user_integrations_chatgpt_workspace_scope", table_name="user_integrations")
    op.drop_index("uq_user_integrations_chatgpt_user_scope", table_name="user_integrations")
