"""Knowledge base management API for Chat Champ.

Provides CRUD operations for knowledge bases and documents,
enabling agents to have custom context for RAG-powered responses.
"""

import uuid
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.settings import get_user_api_keys
from app.core.auth import get_current_user, user_id_to_uuid
from app.db.session import get_db
from app.models.agent import Agent
from app.models.user import User
from app.services.knowledge_base import KnowledgeBaseService

router = APIRouter(prefix="/api/knowledge-bases", tags=["knowledge-bases"])
logger = structlog.get_logger()


# =============================================================================
# Request/Response Models
# =============================================================================


class CreateKnowledgeBaseRequest(BaseModel):
    """Request to create a new knowledge base."""

    agent_id: str = Field(..., description="Agent UUID")
    name: str = Field(..., max_length=200, description="Knowledge base name")
    description: str | None = Field(None, description="Description")
    chunk_size: int = Field(1000, ge=100, le=4000, description="Chunk size in characters")
    chunk_overlap: int = Field(200, ge=0, le=1000, description="Chunk overlap in characters")


class AddTextDocumentRequest(BaseModel):
    """Request to add a text document."""

    content: str = Field(..., min_length=1, description="Document text content")
    source_name: str = Field("text_input", max_length=500, description="Source identifier")
    title: str | None = Field(None, max_length=500, description="Document title")


class AddUrlDocumentRequest(BaseModel):
    """Request to add a URL document."""

    url: str = Field(..., description="URL to fetch and index")
    title: str | None = Field(None, max_length=500, description="Document title")


class SearchRequest(BaseModel):
    """Request to search knowledge base."""

    query: str = Field(..., min_length=1, description="Search query")
    limit: int = Field(5, ge=1, le=20, description="Max results")
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Min similarity")


class KnowledgeBaseResponse(BaseModel):
    """Knowledge base details response."""

    id: str
    agent_id: str
    name: str
    description: str | None
    embedding_model: str
    chunk_size: int
    chunk_overlap: int
    is_active: bool
    document_count: int
    chunk_count: int
    total_characters: int
    created_at: str
    updated_at: str


class DocumentResponse(BaseModel):
    """Document summary response."""

    source_id: str
    source_type: str
    source_name: str
    title: str | None
    chunk_count: int
    total_characters: int
    created_at: str | None


class SearchResultResponse(BaseModel):
    """Search result item."""

    source_name: str
    title: str | None
    content: str
    similarity: float


# =============================================================================
# Helper Functions
# =============================================================================


async def _get_service(
    user: User,
    db: AsyncSession,
    workspace_id: uuid.UUID | None = None,
) -> KnowledgeBaseService:
    """Get knowledge base service with user's OpenAI key."""
    user_uuid = user_id_to_uuid(user.id)
    settings = await get_user_api_keys(user_uuid, db, workspace_id=workspace_id)

    if not settings or not settings.openai_api_key:
        raise HTTPException(status_code=400, detail="OpenAI API key not configured")

    return KnowledgeBaseService(db, settings.openai_api_key)


async def _verify_agent_ownership(
    agent_id: str,
    user: User,
    db: AsyncSession,
) -> Agent:
    """Verify user owns the agent."""
    from sqlalchemy import select

    result = await db.execute(
        select(Agent).where(
            Agent.id == uuid.UUID(agent_id),
            Agent.user_id == user.id,
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


# =============================================================================
# Knowledge Base CRUD
# =============================================================================


@router.post("", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(
    request: CreateKnowledgeBaseRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Create a new knowledge base for an agent."""
    log = logger.bind(endpoint="create_kb", agent_id=request.agent_id, user_id=user.id)

    await _verify_agent_ownership(request.agent_id, user, db)
    service = await _get_service(user, db)

    kb = await service.create_knowledge_base(
        agent_id=uuid.UUID(request.agent_id),
        name=request.name,
        description=request.description,
        chunk_size=request.chunk_size,
        chunk_overlap=request.chunk_overlap,
    )
    await db.commit()

    log.info("knowledge_base_created", kb_id=str(kb.id))

    return {
        "id": str(kb.id),
        "agent_id": str(kb.agent_id),
        "name": kb.name,
        "description": kb.description,
        "embedding_model": kb.embedding_model,
        "chunk_size": kb.chunk_size,
        "chunk_overlap": kb.chunk_overlap,
        "is_active": kb.is_active,
        "document_count": kb.document_count,
        "chunk_count": kb.chunk_count,
        "total_characters": kb.total_characters,
        "created_at": kb.created_at.isoformat(),
        "updated_at": kb.updated_at.isoformat(),
    }


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    kb_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get knowledge base details."""
    service = await _get_service(user, db)
    kb = await service.get_knowledge_base(uuid.UUID(kb_id))

    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    # Verify ownership via agent
    await _verify_agent_ownership(str(kb.agent_id), user, db)

    return {
        "id": str(kb.id),
        "agent_id": str(kb.agent_id),
        "name": kb.name,
        "description": kb.description,
        "embedding_model": kb.embedding_model,
        "chunk_size": kb.chunk_size,
        "chunk_overlap": kb.chunk_overlap,
        "is_active": kb.is_active,
        "document_count": kb.document_count,
        "chunk_count": kb.chunk_count,
        "total_characters": kb.total_characters,
        "created_at": kb.created_at.isoformat(),
        "updated_at": kb.updated_at.isoformat(),
    }


@router.get("/agent/{agent_id}")
async def list_agent_knowledge_bases(
    agent_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """List all knowledge bases for an agent."""
    await _verify_agent_ownership(agent_id, user, db)
    service = await _get_service(user, db)

    kbs = await service.list_knowledge_bases(uuid.UUID(agent_id))

    return [
        {
            "id": str(kb.id),
            "agent_id": str(kb.agent_id),
            "name": kb.name,
            "description": kb.description,
            "is_active": kb.is_active,
            "document_count": kb.document_count,
            "chunk_count": kb.chunk_count,
            "total_characters": kb.total_characters,
            "created_at": kb.created_at.isoformat(),
        }
        for kb in kbs
    ]


@router.delete("/{kb_id}")
async def delete_knowledge_base(
    kb_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Delete a knowledge base and all its documents."""
    service = await _get_service(user, db)
    kb = await service.get_knowledge_base(uuid.UUID(kb_id))

    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    await _verify_agent_ownership(str(kb.agent_id), user, db)

    await service.delete_knowledge_base(uuid.UUID(kb_id))
    await db.commit()

    return {"status": "deleted", "id": kb_id}


# =============================================================================
# Document Management
# =============================================================================


@router.post("/{kb_id}/documents/text")
async def add_text_document(
    kb_id: str,
    request: AddTextDocumentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Add a text document to the knowledge base."""
    log = logger.bind(endpoint="add_text", kb_id=kb_id)

    service = await _get_service(user, db)
    kb = await service.get_knowledge_base(uuid.UUID(kb_id))

    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    await _verify_agent_ownership(str(kb.agent_id), user, db)

    try:
        docs = await service.add_text_document(
            kb_id=uuid.UUID(kb_id),
            content=request.content,
            source_name=request.source_name,
            title=request.title,
        )
        await db.commit()

        log.info("text_document_added", chunks=len(docs))

        return {
            "status": "added",
            "source_id": docs[0].source_id if docs else None,
            "chunk_count": len(docs),
            "total_characters": sum(d.character_count for d in docs),
        }
    except Exception as e:
        log.exception("add_text_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/{kb_id}/documents/url")
async def add_url_document(
    kb_id: str,
    request: AddUrlDocumentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Add a document from URL to the knowledge base."""
    log = logger.bind(endpoint="add_url", kb_id=kb_id, url=request.url)

    service = await _get_service(user, db)
    kb = await service.get_knowledge_base(uuid.UUID(kb_id))

    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    await _verify_agent_ownership(str(kb.agent_id), user, db)

    try:
        docs = await service.add_url_document(
            kb_id=uuid.UUID(kb_id),
            url=request.url,
            title=request.title,
        )
        await db.commit()

        log.info("url_document_added", chunks=len(docs))

        return {
            "status": "added",
            "source_id": docs[0].source_id if docs else None,
            "chunk_count": len(docs),
            "total_characters": sum(d.character_count for d in docs),
        }
    except Exception as e:
        log.exception("add_url_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{kb_id}/documents")
async def list_documents(
    kb_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """List all documents in a knowledge base."""
    service = await _get_service(user, db)
    kb = await service.get_knowledge_base(uuid.UUID(kb_id))

    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    await _verify_agent_ownership(str(kb.agent_id), user, db)

    return await service.list_documents(uuid.UUID(kb_id))


@router.delete("/{kb_id}/documents/{source_id}")
async def delete_document(
    kb_id: str,
    source_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Delete a document from the knowledge base."""
    service = await _get_service(user, db)
    kb = await service.get_knowledge_base(uuid.UUID(kb_id))

    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    await _verify_agent_ownership(str(kb.agent_id), user, db)

    count = await service.delete_document(uuid.UUID(kb_id), source_id)
    await db.commit()

    if count == 0:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"status": "deleted", "source_id": source_id, "chunks_deleted": count}


# =============================================================================
# Search
# =============================================================================


@router.post("/{kb_id}/search")
async def search_knowledge_base(
    kb_id: str,
    request: SearchRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Search for relevant documents in a knowledge base."""
    service = await _get_service(user, db)
    kb = await service.get_knowledge_base(uuid.UUID(kb_id))

    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    await _verify_agent_ownership(str(kb.agent_id), user, db)

    results = await service.search_similar(
        kb_id=uuid.UUID(kb_id),
        query=request.query,
        limit=request.limit,
        similarity_threshold=request.similarity_threshold,
    )

    return [
        {
            "source_name": doc.source_name,
            "title": doc.title,
            "content": doc.content,
            "similarity": round(score, 3),
        }
        for doc, score in results
    ]


@router.post("/agent/{agent_id}/search")
async def search_agent_knowledge(
    agent_id: str,
    request: SearchRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Search across all knowledge bases for an agent."""
    await _verify_agent_ownership(agent_id, user, db)
    service = await _get_service(user, db)

    results = await service.search_across_agent_kbs(
        agent_id=uuid.UUID(agent_id),
        query=request.query,
        limit=request.limit,
        similarity_threshold=request.similarity_threshold,
    )

    return [
        {
            "source_name": doc.source_name,
            "title": doc.title,
            "content": doc.content,
            "similarity": round(score, 3),
        }
        for doc, score in results
    ]
