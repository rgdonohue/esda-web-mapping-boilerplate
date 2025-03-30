from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

from app.core.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

async def setup_cache(app: FastAPI):
    """Initialize Redis cache for the FastAPI application"""
    try:
        redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}" \
            if settings.REDIS_PASSWORD else \
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        
        redis = aioredis.from_url(redis_url, encoding="utf8", decode_responses=True)
        FastAPICache.init(RedisBackend(redis), prefix="esda-cache:")
        
        logger.info(f"Cache initialized with Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        return redis
    except Exception as e:
        logger.error(f"Failed to initialize Redis cache: {str(e)}")
        logger.warning("Application will continue without caching")
        return None

# Export the cache decorator with default TTL from settings
def cached(expire: int = None, namespace: str = None, key_builder=None):
    """Decorator for caching API responses with default TTL from settings"""
    return cache(
        expire=expire or settings.CACHE_TTL,
        namespace=namespace,
        key_builder=key_builder
    )