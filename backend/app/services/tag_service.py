"""Tag CRUD, attach/detach on contacts and leads."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag
from app.utils.exceptions import ConflictError
from app.schemas.tag import TagCreate, TagUpdate


async def create(session: AsyncSession, data: TagCreate) -> Tag:
    result = await session.execute(select(Tag).where(Tag.name == data.name))
    if result.scalar_one_or_none():
        raise ConflictError("Tag with this name already exists")
    tag = Tag(name=data.name)
    session.add(tag)
    await session.flush()
    await session.refresh(tag)
    return tag


async def get_by_id(session: AsyncSession, tag_id: UUID) -> Tag | None:
    result = await session.execute(select(Tag).where(Tag.id == tag_id))
    return result.scalar_one_or_none()


async def get_by_name(session: AsyncSession, name: str) -> Tag | None:
    result = await session.execute(select(Tag).where(Tag.name == name))
    return result.scalar_one_or_none()


async def list_all(session: AsyncSession) -> list[Tag]:
    result = await session.execute(select(Tag).order_by(Tag.name))
    return list(result.scalars().all())


async def update(session: AsyncSession, tag_id: UUID, data: TagUpdate) -> Tag | None:
    tag = await get_by_id(session, tag_id)
    if not tag:
        return None
    if data.name is not None:
        existing = await get_by_name(session, data.name)
        if existing and existing.id != tag_id:
            raise ConflictError("Tag with this name already exists")
        tag.name = data.name
    await session.flush()
    await session.refresh(tag)
    return tag


async def delete(session: AsyncSession, tag_id: UUID) -> bool:
    tag = await get_by_id(session, tag_id)
    if not tag:
        return False
    await session.delete(tag)
    await session.flush()
    return True
