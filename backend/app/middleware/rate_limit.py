"""Redis-backed rate limiting per IP (and optionally per user)."""
from datetime import datetime, timezone
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.redis.client import get_redis
from app.redis.keys import rate_limit_key
from app.config import get_settings

settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip rate limit for health and docs
        if request.url.path in ("/health", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)
        client_ip = request.client.host if request.client else "unknown"
        minute_bucket = datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
        key = rate_limit_key(client_ip, minute_bucket)
        redis = await get_redis()
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, 60)
        if count > settings.rate_limit_requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={"data": None, "message": "Too many requests", "success": False},
            )
        return await call_next(request)
