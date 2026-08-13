"""Health check endpoints."""

import logging

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.redis import get_redis
from app.db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@router.get("/health/db")
async def health_check_db(response: Response, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """Database health check endpoint."""
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.exception("Database health check failed")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unhealthy", "database": str(e)}


@router.get("/health/redis")
async def health_check_redis(response: Response) -> dict[str, str]:
    """Redis health check endpoint."""
    try:
        redis = await get_redis()
        await redis.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        logger.exception("Redis health check failed")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unhealthy", "redis": str(e)}


@router.get("/health/cors")
async def health_check_cors() -> dict[str, list[str] | bool]:
    """Debug endpoint to check CORS configuration."""
    return {
        "cors_origins": settings.CORS_ORIGINS,
        "cors_credentials": settings.CORS_ALLOW_CREDENTIALS,
        "cors_methods": settings.CORS_ALLOW_METHODS,
        "cors_headers": settings.CORS_ALLOW_HEADERS,
    }
