"""Knowledge base models for Chat Champ RAG functionality.

Provides document storage with vector embeddings for semantic search
and context injection into chat conversations.
"""

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.agent import Agent

# OpenAI text-embedding-3-small produces 1536-dimensional vectors
EMBEDDING_DIMENSIONS = 1536


class KnowledgeBase(Base):
    """A knowledge base containing documents for an agent.

    Each agent can have multiple knowledge bases, each with
    a collection of documents for RAG context.
    """

    __tablename__ = "knowledge_bases"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Agent this knowledge base belongs to",
    )

    # Knowledge base info
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Knowledge base name",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Description of what this knowledge base contains",
    )

    # Configuration
    embedding_model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="text-embedding-3-small",
        comment="Model used for generating embeddings",
    )
    chunk_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1000,
        comment="Target chunk size in characters for document splitting",
    )
    chunk_overlap: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=200,
        comment="Overlap between chunks in characters",
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
        comment="Whether this knowledge base is active for queries",
    )

    # Statistics
    document_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total number of source documents",
    )
    chunk_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total number of chunks/embeddings",
    )
    total_characters: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total characters across all documents",
    )

    # Timestamps
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

    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", lazy="selectin")
    documents: Mapped[list["KnowledgeDocument"]] = relationship(
        "KnowledgeDocument",
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<KnowledgeBase(id={self.id}, name={self.name}, "
            f"documents={self.document_count}, chunks={self.chunk_count})>"
        )


class KnowledgeDocument(Base):
    """A document chunk with vector embedding.

    Documents are split into chunks for better retrieval.
    Each chunk has its own embedding for similarity search.
    """

    __tablename__ = "knowledge_documents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("knowledge_bases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Parent knowledge base",
    )

    # Source information
    source_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Source type: pdf, url, text, file",
    )
    source_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Original filename or URL",
    )
    source_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="Hash ID to group chunks from same source",
    )

    # Chunk content
    title: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Section title if available",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Chunk text content",
    )
    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Index of this chunk within the source document",
    )

    # Vector embedding
    embedding: Mapped[list[float]] = mapped_column(
        Vector(EMBEDDING_DIMENSIONS),
        nullable=True,
        comment="Vector embedding for similarity search",
    )

    # Metadata
    extra_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Additional metadata: page_number, headers, etc.",
    )
    character_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of characters in this chunk",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    knowledge_base: Mapped["KnowledgeBase"] = relationship(
        "KnowledgeBase", back_populates="documents"
    )

    def __repr__(self) -> str:
        preview_length = 50
        if len(self.content) > preview_length:
            content_preview = self.content[:preview_length] + "..."
        else:
            content_preview = self.content
        return (
            f"<KnowledgeDocument(id={self.id}, source={self.source_name}, "
            f"chunk={self.chunk_index}, content='{content_preview}')>"
        )
