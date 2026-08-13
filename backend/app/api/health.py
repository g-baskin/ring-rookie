"""Health check endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.redis import get_redis
from app.db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
@router.get("/health/live")
async def health_check() -> dict[str, str]:
    """Report process liveness without checking external dependencies."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


async def _database_is_ready(db: AsyncSession) -> bool:
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
    except Exception:
        logger.exception("Database health check failed")
        return False
    return True


async def _redis_is_ready(redis: Any) -> bool:
    try:
        await redis.ping()
    except Exception:
        logger.exception("Redis health check failed")
        return False
    return True


@router.get("/health/ready")
async def readiness_check(
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis),
) -> dict[str, str]:
    """Report readiness only when PostgreSQL and Redis respond."""
    database_ready = await _database_is_ready(db)
    redis_ready = await _redis_is_ready(redis)

    if not database_ready or not redis_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "unhealthy",
            "database": "connected" if database_ready else "unavailable",
            "redis": "connected" if redis_ready else "unavailable",
        }

    return {"status": "healthy", "database": "connected", "redis": "connected"}


@router.get("/health/db")
async def health_check_db(response: Response, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """Database health check endpoint."""
    if await _database_is_ready(db):
        return {"status": "healthy", "database": "connected"}

    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": "unhealthy", "database": "unavailable"}


@router.get("/health/redis")
async def health_check_redis(response: Response, redis: Any = Depends(get_redis)) -> dict[str, str]:
    """Redis health check endpoint."""
    if await _redis_is_ready(redis):
        return {"status": "healthy", "redis": "connected"}

    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": "unhealthy", "redis": "unavailable"}


@router.get("/health/cors")
async def health_check_cors() -> dict[str, list[str] | bool]:
    """Debug endpoint to check CORS configuration."""
    return {
        "cors_origins": settings.CORS_ORIGINS,
        "cors_credentials": settings.CORS_ALLOW_CREDENTIALS,
        "cors_methods": settings.CORS_ALLOW_METHODS,
        "cors_headers": settings.CORS_ALLOW_HEADERS,
    }
