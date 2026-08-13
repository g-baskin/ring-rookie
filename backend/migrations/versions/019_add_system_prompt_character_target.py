"""Add configurable system prompt character target.

Revision ID: 019_add_prompt_target
Revises: 018_add_effect_claims
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "019_add_prompt_target"
down_revision: str | None = "018_add_effect_claims"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add and backfill the prompt target for all agents."""
    op.add_column(
        "agents",
        sa.Column(
            "system_prompt_character_target",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("5000"),
        ),
    )
    op.create_check_constraint(
        "ck_agents_system_prompt_character_target_range",
        "agents",
        "system_prompt_character_target BETWEEN 1000 AND 20000",
    )


def downgrade() -> None:
    """Remove the prompt character target."""
    op.drop_constraint("ck_agents_system_prompt_character_target_range", "agents", type_="check")
    op.drop_column("agents", "system_prompt_character_target")
