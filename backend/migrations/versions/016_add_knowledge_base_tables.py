"""Add knowledge base tables for Chat Champ RAG.

Revision ID: 016_add_knowledge_base_tables
Revises: 015_add_chat_champ_conversations
Create Date: 2025-01-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "016_add_knowledge_base_tables"
down_revision: str | None = "015_add_chat_champ_conversations"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# OpenAI text-embedding-3-small produces 1536-dimensional vectors
EMBEDDING_DIMENSIONS = 1536


def upgrade() -> None:
    """Create knowledge base tables with pgvector support."""
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create knowledge_bases table
    op.create_table(
        "knowledge_bases",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "agent_id",
            sa.Uuid(),
            nullable=False,
            comment="Agent this knowledge base belongs to",
        ),
        sa.Column(
            "name",
            sa.String(200),
            nullable=False,
            comment="Knowledge base name",
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
            comment="Description of what this knowledge base contains",
        ),
        sa.Column(
            "embedding_model",
            sa.String(100),
            nullable=False,
            server_default="text-embedding-3-small",
            comment="Model used for generating embeddings",
        ),
        sa.Column(
            "chunk_size",
            sa.Integer(),
            nullable=False,
            server_default="1000",
            comment="Target chunk size in characters for document splitting",
        ),
        sa.Column(
            "chunk_overlap",
            sa.Integer(),
            nullable=False,
            server_default="200",
            comment="Overlap between chunks in characters",
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default="true",
            comment="Whether this knowledge base is active for queries",
        ),
        sa.Column(
            "document_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Total number of source documents",
        ),
        sa.Column(
            "chunk_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Total number of chunks/embeddings",
        ),
        sa.Column(
            "total_characters",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Total characters across all documents",
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

    # Create indexes for knowledge_bases
    op.create_index("ix_knowledge_bases_agent_id", "knowledge_bases", ["agent_id"])

    # Create knowledge_documents table
    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "knowledge_base_id",
            sa.Uuid(),
            nullable=False,
            comment="Parent knowledge base",
        ),
        sa.Column(
            "source_type",
            sa.String(20),
            nullable=False,
            comment="Source type: pdf, url, text, file",
        ),
        sa.Column(
            "source_name",
            sa.String(500),
            nullable=False,
            comment="Original filename or URL",
        ),
        sa.Column(
            "source_id",
            sa.String(64),
            nullable=False,
            comment="Hash ID to group chunks from same source",
        ),
        sa.Column(
            "title",
            sa.String(500),
            nullable=True,
            comment="Section title if available",
        ),
        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
            comment="Chunk text content",
        ),
        sa.Column(
            "chunk_index",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Index of this chunk within the source document",
        ),
        sa.Column(
            "embedding",
            Vector(EMBEDDING_DIMENSIONS),
            nullable=True,
            comment="Vector embedding for similarity search",
        ),
        sa.Column(
            "extra_data",
            JSONB(),
            nullable=False,
            server_default="{}",
            comment="Additional metadata: page_number, headers, etc.",
        ),
        sa.Column(
            "character_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Number of characters in this chunk",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["knowledge_base_id"],
            ["knowledge_bases.id"],
            ondelete="CASCADE",
        ),
    )

    # Create indexes for knowledge_documents
    op.create_index(
        "ix_knowledge_documents_knowledge_base_id",
        "knowledge_documents",
        ["knowledge_base_id"],
    )
    op.create_index(
        "ix_knowledge_documents_source_id",
        "knowledge_documents",
        ["source_id"],
    )

    # Create IVFFlat index for vector similarity search
    # Using 100 lists is good for up to ~1M vectors
    op.execute(
        """
        CREATE INDEX ix_knowledge_documents_embedding
        ON knowledge_documents
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
        """
    )


def downgrade() -> None:
    """Drop knowledge base tables."""
    # Drop knowledge_documents indexes and table
    op.execute("DROP INDEX IF EXISTS ix_knowledge_documents_embedding")
    op.drop_index("ix_knowledge_documents_source_id", "knowledge_documents")
    op.drop_index("ix_knowledge_documents_knowledge_base_id", "knowledge_documents")
    op.drop_table("knowledge_documents")

    # Drop knowledge_bases indexes and table
    op.drop_index("ix_knowledge_bases_agent_id", "knowledge_bases")
    op.drop_table("knowledge_bases")

    # Note: We don't drop the vector extension as other tables might use it
