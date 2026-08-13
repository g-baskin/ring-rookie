"""merge current migration heads

Revision ID: ca97ba39b920
Revises: 016_add_knowledge_base_tables, 017_add_usage_metering_tables, 2aeb78a98185
Create Date: 2026-08-13 00:13:17.802099

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "ca97ba39b920"
down_revision: Union[str, Sequence[str], None] = (
    "016_add_knowledge_base_tables",
    "017_add_usage_metering_tables",
    "2aeb78a98185",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
