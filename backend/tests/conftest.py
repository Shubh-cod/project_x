"""Pytest fixtures: test client, DB, Redis."""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Import all models so Base.metadata.create_all creates every table
# (activities, leads, deals, tasks, notes, tags, email_logs, etc.)
import app.models  # noqa: F401

# Import redis client module so we can reset singletons between tests
import app.redis.client as _redis_mod

from app.main import app as fastapi_app
from app.db.base import Base, get_db
from app.config import get_settings

# Use in-memory SQLite for tests (or same PG with test DB)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"



@pytest.fixture(scope="function")
async def db_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def override_get_db(db_session):
    async def _get_db():
        yield db_session
    return _get_db


@pytest.fixture
async def client(override_get_db):
    fastapi_app.dependency_overrides[get_db] = override_get_db
    # Flush rate-limit keys so past test runs don't cause 429 errors.
    # We get a fresh Redis connection here (setup) and clean counters.
    from app.redis.client import get_redis
    redis = await get_redis()
    keys = []
    async for k in redis.scan_iter(match="ratelimit:*"):
        keys.append(k)
    if keys:
        await redis.delete(*keys)
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    fastapi_app.dependency_overrides.clear()
    # Reset the Redis client singleton so the next test (which gets a fresh
    # event loop) doesn't try to reuse a connection bound to the old loop.
    # Without this, the 2nd+ test crashes with "Event loop is closed".
    if _redis_mod._client:
        try:
            await _redis_mod._client.aclose()
        except Exception:
            pass
    _redis_mod._client = None
    if _redis_mod._pool:
        try:
            await _redis_mod._pool.disconnect()
        except Exception:
            pass
    _redis_mod._pool = None
