"""add durable effect claims and call identity uniqueness

Revision ID: 018_add_effect_claims
Revises: 1df9973696e0
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "018_add_effect_claims"
down_revision: str | None = "1df9973696e0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "effect_claims",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("scope_key", sa.String(64), nullable=False),
        sa.Column("namespace", sa.String(100), nullable=False),
        sa.Column("digest", sa.String(64), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("first_attempt_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("response", sa.Text()),
        sa.Column("provider_ref", sa.String(255)),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scope_key", "namespace", "digest", name="uq_effect_claim_identity"),
    )
    op.create_unique_constraint(
        "uq_call_records_provider_call_id", "call_records", ["provider", "provider_call_id"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_call_records_provider_call_id", "call_records", type_="unique")
    op.drop_table("effect_claims")
