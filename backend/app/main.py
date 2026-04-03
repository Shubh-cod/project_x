"""FastAPI app init, middleware, router inclusion."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.v1.router import api_router
from app.utils.exceptions import exception_response
from app.db.base import engine, AsyncSessionLocal
from app.redis.client import close_redis
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("novacrm")

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create automation_rules table if it doesn't exist (additive, no Alembic)
    try:
        from sqlalchemy import text
        async with engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS automation_rules (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(255) NOT NULL,
                    trigger_event VARCHAR(50) NOT NULL,
                    conditions JSONB,
                    action_type VARCHAR(50) NOT NULL DEFAULT 'create_task',
                    action_config JSONB,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """))
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_automation_rules_trigger_event
                ON automation_rules (trigger_event)
            """))
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_automation_rules_name
                ON automation_rules (name)
            """))
        logger.info("automation_rules table ensured")
    except Exception as e:
        logger.warning(f"Could not ensure automation_rules table: {e}")

    # Seed default automation rules
    try:
        from app.services.automation_service import seed_default_rules
        async with AsyncSessionLocal() as session:
            await seed_default_rules(session)
            await session.commit()
    except Exception as e:
        logger.warning(f"Could not seed automation rules: {e}")

    yield
    await close_redis()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_exception_handler(Exception, exception_response)

app.include_router(api_router)


@app.get("/health")
async def health():
    """Health check: status, db, redis."""
    from sqlalchemy import text
    from app.redis.client import get_redis
    status = "ok"
    db_ok = "ok"
    redis_ok = "ok"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception as e:
        db_ok = str(e)
        status = "degraded"
    try:
        r = await get_redis()
        await r.ping()
    except Exception as e:
        redis_ok = str(e)
        status = "degraded"
    return {"status": status, "db": db_ok, "redis": redis_ok}
