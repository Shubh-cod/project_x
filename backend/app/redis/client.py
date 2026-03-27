"""Redis async client setup."""
from typing import Optional

import redis.asyncio as redis
from app.config import get_settings

_settings = get_settings()
_pool: Optional[redis.ConnectionPool] = None
_client: Optional[redis.Redis] = None


def get_redis_pool() -> redis.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = redis.ConnectionPool.from_url(
            _settings.redis_url,
            password=_settings.redis_password or None,
            decode_responses=True,
            max_connections=20,
        )
    return _pool


async def get_redis() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.Redis(connection_pool=get_redis_pool())
    return _client


async def close_redis() -> None:
    global _client, _pool
    if _client:
        await _client.aclose()
        _client = None
    if _pool:
        await _pool.disconnect()
        _pool = None
