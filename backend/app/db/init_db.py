"""DB initialization and optional seed."""
import asyncio
from app.db.base import engine, Base
from app.models import (
    User,
    Tag,
    Contact,
    Lead,
    Deal,
    Task,
    Note,
    Activity,
    EmailLog,
)
from app.models.tag import contact_tags, lead_tags


async def init_db():
    """Create all tables. Safe to call multiple times (creates only if not exist)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_dev():
    """Optional: seed a dev user and sample data. Call after init_db."""
    from app.db.base import AsyncSessionLocal
    from app.utils.security import get_password_hash
    from app.utils.enums import UserRole

    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.email == "admin@novacrm.local"))
        if result.scalar_one_or_none():
            return
        admin = User(
            email="admin@novacrm.local",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            role=UserRole.admin,
        )
        session.add(admin)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(init_db())
    # asyncio.run(seed_dev())
