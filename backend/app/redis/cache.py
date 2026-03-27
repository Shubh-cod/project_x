"""Generic cache get/set/invalidate helpers."""
import json
from typing import Any, Optional

import redis.asyncio as redis

from app.redis.client import get_redis


async def cache_get(key: str) -> Optional[str]:
    r = await get_redis()
    return await r.get(key)


async def cache_set(key: str, value: str, ttl_seconds: int) -> None:
    r = await get_redis()
    await r.setex(key, ttl_seconds, value)


async def cache_get_json(key: str) -> Optional[Any]:
    raw = await cache_get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


async def cache_set_json(key: str, value: Any, ttl_seconds: int) -> None:
    await cache_set(key, json.dumps(value, default=str), ttl_seconds)


async def cache_delete(key: str) -> None:
    r = await get_redis()
    await r.delete(key)


async def cache_delete_pattern(pattern: str) -> None:
    """Delete all keys matching pattern (e.g. 'search:*')."""
    r = await get_redis()
    keys = []
    async for k in r.scan_iter(match=pattern):
        keys.append(k)
    if keys:
        await r.delete(*keys)
