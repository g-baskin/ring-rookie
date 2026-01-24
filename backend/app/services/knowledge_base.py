"""Knowledge base service for Chat Champ RAG functionality.

Handles document processing, embedding generation, and semantic search
for context injection into chat conversations.
"""

import hashlib
import re
import uuid
from typing import Any

import httpx
import structlog
from openai import AsyncOpenAI
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge_base import (
    KnowledgeBase,
    KnowledgeDocument,
)

logger = structlog.get_logger()

# Default embedding model
EMBEDDING_MODEL = "text-embedding-3-small"

# Chunk settings
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200
MAX_CHUNKS_PER_QUERY = 5


class KnowledgeBaseService:
    """Service for managing knowledge bases and documents."""

    def __init__(self, db: AsyncSession, openai_api_key: str) -> None:
        """Initialize the service.

        Args:
            db: Database session
            openai_api_key: OpenAI API key for embeddings
        """
        self.db = db
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.log = logger.bind(service="knowledge_base")

    async def create_knowledge_base(
        self,
        agent_id: uuid.UUID,
        name: str,
        description: str | None = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> KnowledgeBase:
        """Create a new knowledge base for an agent."""
        kb = KnowledgeBase(
            agent_id=agent_id,
            name=name,
            description=description,
            embedding_model=EMBEDDING_MODEL,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        self.db.add(kb)
        await self.db.flush()
        self.log.info("knowledge_base_created", kb_id=str(kb.id), name=name)
        return kb

    async def get_knowledge_base(
        self,
        kb_id: uuid.UUID,
        agent_id: uuid.UUID | None = None,
    ) -> KnowledgeBase | None:
        """Get a knowledge base by ID, optionally verifying agent ownership."""
        query = select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
        if agent_id:
            query = query.where(KnowledgeBase.agent_id == agent_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_knowledge_bases(self, agent_id: uuid.UUID) -> list[KnowledgeBase]:
        """List all knowledge bases for an agent."""
        result = await self.db.execute(
            select(KnowledgeBase)
            .where(KnowledgeBase.agent_id == agent_id)
            .order_by(KnowledgeBase.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_knowledge_base(self, kb_id: uuid.UUID) -> bool:
        """Delete a knowledge base and all its documents."""
        kb = await self.get_knowledge_base(kb_id)
        if not kb:
            return False
        await self.db.delete(kb)
        self.log.info("knowledge_base_deleted", kb_id=str(kb_id))
        return True

    # =========================================================================
    # Document Processing
    # =========================================================================

    def _generate_source_id(self, source_type: str, source_name: str, content: str) -> str:
        """Generate a unique source ID for deduplication."""
        data = f"{source_type}:{source_name}:{len(content)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _chunk_text(
        self,
        text: str,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> list[str]:
        """Split text into overlapping chunks.

        Uses sentence-aware splitting to avoid cutting mid-sentence.
        """
        # Clean the text
        text = re.sub(r"\s+", " ", text).strip()

        if len(text) <= chunk_size:
            return [text] if text else []

        # Split into sentences
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks: list[str] = []
        current_chunk: list[str] = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            if current_length + sentence_length > chunk_size and current_chunk:
                # Save current chunk
                chunk_text = " ".join(current_chunk)
                chunks.append(chunk_text)

                # Start new chunk with overlap
                overlap_sentences: list[str] = []
                overlap_length = 0
                for s in reversed(current_chunk):
                    if overlap_length + len(s) <= chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_length += len(s) + 1
                    else:
                        break

                current_chunk = overlap_sentences
                current_length = sum(len(s) for s in current_chunk) + len(current_chunk)

            current_chunk.append(sentence)
            current_length += sentence_length + 1

        # Add final chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    async def _generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for a text chunk."""
        response = await self.client.embeddings.create(model=EMBEDDING_MODEL, input=text)
        return response.data[0].embedding

    async def _generate_embeddings_batch(
        self,
        texts: list[str],
        batch_size: int = 100,
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts in batches."""
        embeddings: list[list[float]] = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = await self.client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
            embeddings.extend([item.embedding for item in response.data])

        return embeddings

    async def add_text_document(
        self,
        kb_id: uuid.UUID,
        content: str,
        source_name: str = "text_input",
        title: str | None = None,
    ) -> list[KnowledgeDocument]:
        """Add a text document to the knowledge base."""
        kb = await self.get_knowledge_base(kb_id)
        if not kb:
            msg = f"Knowledge base {kb_id} not found"
            raise ValueError(msg)

        source_id = self._generate_source_id("text", source_name, content)

        # Check for existing documents from same source
        existing = await self.db.execute(
            select(KnowledgeDocument).where(
                KnowledgeDocument.knowledge_base_id == kb_id,
                KnowledgeDocument.source_id == source_id,
            )
        )
        if existing.scalar_one_or_none():
            self.log.info("document_already_exists", source_id=source_id)
            # Delete existing and re-add
            await self.db.execute(
                delete(KnowledgeDocument).where(
                    KnowledgeDocument.knowledge_base_id == kb_id,
                    KnowledgeDocument.source_id == source_id,
                )
            )

        # Chunk the content
        chunks = self._chunk_text(content, kb.chunk_size, kb.chunk_overlap)
        if not chunks:
            return []

        # Generate embeddings
        self.log.info("generating_embeddings", chunk_count=len(chunks))
        embeddings = await self._generate_embeddings_batch(chunks)

        # Create documents
        documents: list[KnowledgeDocument] = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings, strict=False)):
            doc = KnowledgeDocument(
                knowledge_base_id=kb_id,
                source_type="text",
                source_name=source_name,
                source_id=source_id,
                title=title,
                content=chunk,
                chunk_index=i,
                embedding=embedding,
                character_count=len(chunk),
            )
            self.db.add(doc)
            documents.append(doc)

        # Update knowledge base stats
        kb.document_count += 1
        kb.chunk_count += len(documents)
        kb.total_characters += len(content)

        await self.db.flush()
        self.log.info(
            "text_document_added",
            kb_id=str(kb_id),
            source_name=source_name,
            chunks=len(documents),
        )
        return documents

    async def add_url_document(
        self,
        kb_id: uuid.UUID,
        url: str,
        title: str | None = None,
    ) -> list[KnowledgeDocument]:
        """Add a document from a URL to the knowledge base."""
        kb = await self.get_knowledge_base(kb_id)
        if not kb:
            msg = f"Knowledge base {kb_id} not found"
            raise ValueError(msg)

        # Fetch URL content
        self.log.info("fetching_url", url=url)
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            content = response.text

        # Extract text from HTML (basic extraction)
        content = self._extract_text_from_html(content)

        source_id = self._generate_source_id("url", url, content)

        # Check for existing documents from same source
        existing = await self.db.execute(
            select(KnowledgeDocument).where(
                KnowledgeDocument.knowledge_base_id == kb_id,
                KnowledgeDocument.source_id == source_id,
            )
        )
        if existing.scalar_one_or_none():
            # Delete existing and re-add
            await self.db.execute(
                delete(KnowledgeDocument).where(
                    KnowledgeDocument.knowledge_base_id == kb_id,
                    KnowledgeDocument.source_id == source_id,
                )
            )

        # Chunk and process
        chunks = self._chunk_text(content, kb.chunk_size, kb.chunk_overlap)
        if not chunks:
            return []

        embeddings = await self._generate_embeddings_batch(chunks)

        documents: list[KnowledgeDocument] = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings, strict=False)):
            doc = KnowledgeDocument(
                knowledge_base_id=kb_id,
                source_type="url",
                source_name=url,
                source_id=source_id,
                title=title or url,
                content=chunk,
                chunk_index=i,
                embedding=embedding,
                character_count=len(chunk),
                extra_data={"url": url},
            )
            self.db.add(doc)
            documents.append(doc)

        kb.document_count += 1
        kb.chunk_count += len(documents)
        kb.total_characters += len(content)

        await self.db.flush()
        self.log.info("url_document_added", kb_id=str(kb_id), url=url, chunks=len(documents))
        return documents

    def _extract_text_from_html(self, html: str) -> str:
        """Extract plain text from HTML content."""
        # Remove script and style elements
        html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)

        # Remove HTML tags
        text = re.sub(r"<[^>]+>", " ", html)

        # Decode HTML entities (basic)
        text = text.replace("&nbsp;", " ")
        text = text.replace("&amp;", "&")
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
        text = text.replace("&quot;", '"')

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    async def delete_document(self, kb_id: uuid.UUID, source_id: str) -> int:
        """Delete all chunks for a document by source_id."""
        # Get count first for stats update
        count_result = await self.db.execute(
            select(func.count())
            .select_from(KnowledgeDocument)
            .where(
                KnowledgeDocument.knowledge_base_id == kb_id,
                KnowledgeDocument.source_id == source_id,
            )
        )
        count = count_result.scalar() or 0

        if count > 0:
            # Get character count for stats
            char_result = await self.db.execute(
                select(func.sum(KnowledgeDocument.character_count)).where(
                    KnowledgeDocument.knowledge_base_id == kb_id,
                    KnowledgeDocument.source_id == source_id,
                )
            )
            total_chars = char_result.scalar() or 0

            # Delete documents
            await self.db.execute(
                delete(KnowledgeDocument).where(
                    KnowledgeDocument.knowledge_base_id == kb_id,
                    KnowledgeDocument.source_id == source_id,
                )
            )

            # Update stats
            kb = await self.get_knowledge_base(kb_id)
            if kb:
                kb.document_count -= 1
                kb.chunk_count -= count
                kb.total_characters -= total_chars

            self.log.info("document_deleted", kb_id=str(kb_id), source_id=source_id, chunks=count)

        return count

    # =========================================================================
    # Search & RAG
    # =========================================================================

    async def search_similar(
        self,
        kb_id: uuid.UUID,
        query: str,
        limit: int = MAX_CHUNKS_PER_QUERY,
        similarity_threshold: float = 0.7,
    ) -> list[tuple[KnowledgeDocument, float]]:
        """Search for similar documents using vector similarity.

        Returns list of (document, similarity_score) tuples.
        """
        # Generate query embedding
        query_embedding = await self._generate_embedding(query)

        # Use pgvector cosine similarity
        # cosine_distance returns 1 - similarity, so we use 1 - distance for similarity
        result = await self.db.execute(
            select(
                KnowledgeDocument,
                (1 - KnowledgeDocument.embedding.cosine_distance(query_embedding)).label(
                    "similarity"
                ),
            )
            .where(
                KnowledgeDocument.knowledge_base_id == kb_id,
                KnowledgeDocument.embedding.isnot(None),
            )
            .order_by(KnowledgeDocument.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )

        results: list[tuple[KnowledgeDocument, float]] = []
        for row in result:
            doc = row[0]
            similarity = float(row[1])
            if similarity >= similarity_threshold:
                results.append((doc, similarity))

        self.log.info(
            "search_complete",
            kb_id=str(kb_id),
            query_length=len(query),
            results=len(results),
        )
        return results

    async def search_across_agent_kbs(
        self,
        agent_id: uuid.UUID,
        query: str,
        limit: int = MAX_CHUNKS_PER_QUERY,
        similarity_threshold: float = 0.7,
    ) -> list[tuple[KnowledgeDocument, float]]:
        """Search across all active knowledge bases for an agent."""
        # Get all active KB IDs for the agent
        kb_result = await self.db.execute(
            select(KnowledgeBase.id).where(
                KnowledgeBase.agent_id == agent_id,
                KnowledgeBase.is_active.is_(True),
            )
        )
        kb_ids = [row[0] for row in kb_result]

        if not kb_ids:
            return []

        # Generate query embedding
        query_embedding = await self._generate_embedding(query)

        # Search across all KBs
        result = await self.db.execute(
            select(
                KnowledgeDocument,
                (1 - KnowledgeDocument.embedding.cosine_distance(query_embedding)).label(
                    "similarity"
                ),
            )
            .where(
                KnowledgeDocument.knowledge_base_id.in_(kb_ids),
                KnowledgeDocument.embedding.isnot(None),
            )
            .order_by(KnowledgeDocument.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )

        results: list[tuple[KnowledgeDocument, float]] = []
        for row in result:
            doc = row[0]
            similarity = float(row[1])
            if similarity >= similarity_threshold:
                results.append((doc, similarity))

        return results

    def build_rag_context(
        self,
        documents: list[tuple[KnowledgeDocument, float]],
        max_context_length: int = 3000,
    ) -> str:
        """Build RAG context string from search results.

        Returns formatted context to inject into the system prompt.
        """
        if not documents:
            return ""

        context_parts: list[str] = []
        current_length = 0

        for doc, similarity in documents:
            # Format each chunk with source info
            source_info = f"[Source: {doc.source_name}"
            if doc.title:
                source_info += f" - {doc.title}"
            source_info += f" (relevance: {similarity:.0%})]"

            chunk_text = f"{source_info}\n{doc.content}"

            if current_length + len(chunk_text) > max_context_length:
                break

            context_parts.append(chunk_text)
            current_length += len(chunk_text) + 2  # +2 for separator

        if not context_parts:
            return ""

        context = "\n\n".join(context_parts)
        return f"""
Use the following context to answer the user's question:

---
{context}
---

If the context doesn't contain relevant information, you can still answer based on your general knowledge, but mention that the information isn't in the provided documents.
"""

    async def get_rag_context_for_query(
        self,
        agent_id: uuid.UUID,
        query: str,
        max_chunks: int = MAX_CHUNKS_PER_QUERY,
        max_context_length: int = 3000,
    ) -> str:
        """Get RAG context for a user query.

        This is the main method to call when processing a chat message.
        """
        results = await self.search_across_agent_kbs(
            agent_id=agent_id,
            query=query,
            limit=max_chunks,
        )
        return self.build_rag_context(results, max_context_length)

    # =========================================================================
    # Stats & Info
    # =========================================================================

    async def list_documents(self, kb_id: uuid.UUID) -> list[dict[str, Any]]:
        """List all unique documents (sources) in a knowledge base."""
        result = await self.db.execute(
            select(
                KnowledgeDocument.source_id,
                KnowledgeDocument.source_type,
                KnowledgeDocument.source_name,
                KnowledgeDocument.title,
                func.count(KnowledgeDocument.id).label("chunk_count"),
                func.sum(KnowledgeDocument.character_count).label("total_chars"),
                func.min(KnowledgeDocument.created_at).label("created_at"),
            )
            .where(KnowledgeDocument.knowledge_base_id == kb_id)
            .group_by(
                KnowledgeDocument.source_id,
                KnowledgeDocument.source_type,
                KnowledgeDocument.source_name,
                KnowledgeDocument.title,
            )
            .order_by(func.min(KnowledgeDocument.created_at).desc())
        )

        return [
            {
                "source_id": row.source_id,
                "source_type": row.source_type,
                "source_name": row.source_name,
                "title": row.title,
                "chunk_count": row.chunk_count,
                "total_characters": row.total_chars,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in result
        ]
