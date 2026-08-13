"""add durable worker items

Revision ID: 019_add_worker_items
Revises: 018_add_effect_claims
"""

from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = "019_add_worker_items"
down_revision: str | None = "018_add_effect_claims"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "worker_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("scope_key", sa.String(64), nullable=False),
        sa.Column("namespace", sa.String(100), nullable=False),
        sa.Column("item_digest", sa.String(64), nullable=False),
        sa.Column("payload_ref", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("max_age_seconds", sa.Integer(), nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("lease_owner", sa.String(100)),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True)),
        sa.Column("trace_id", sa.String(64)),
        sa.Column("exception_type", sa.String(100)),
        sa.Column("last_error", sa.String(512)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("dead_at", sa.DateTime(timezone=True)),
        sa.Column("replay_actor", sa.String(100)),
        sa.Column("replay_reason", sa.String(255)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "scope_key", "namespace", "item_digest", name="uq_worker_item_identity"
        ),
    )
    op.create_index(
        "ix_worker_items_claim", "worker_items", ["namespace", "status", "available_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_worker_items_claim", table_name="worker_items")
    op.drop_table("worker_items")
