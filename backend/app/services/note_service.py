"""Note CRUD, polymorphic attachment to contact/lead/deal."""
from uuid import UUID
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.note import Note
from app.utils.pagination import paginate
from app.services.activity_service import log as activity_log
from app.schemas.note import NoteCreate, NoteUpdate


async def create(
    session: AsyncSession,
    data: NoteCreate,
    user_id: Optional[UUID] = None,
) -> Note:
    note = Note(
        content=data.content,
        entity_type=data.entity_type,
        entity_id=data.entity_id,
        created_by=user_id,
    )
    session.add(note)
    await session.flush()
    await activity_log(session, data.entity_type, data.entity_id, "note_added", user_id, {"note_id": str(note.id)})
    await session.refresh(note)
    return note


async def get_by_id(session: AsyncSession, note_id: UUID) -> Note | None:
    result = await session.execute(select(Note).where(Note.id == note_id))
    return result.scalar_one_or_none()


async def list_by_entity(
    session: AsyncSession,
    entity_type: str,
    entity_id: UUID,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Note], int]:
    q = (
        select(Note)
        .where(Note.entity_type == entity_type, Note.entity_id == entity_id)
        .order_by(Note.created_at.desc())
    )
    return await paginate(session, q, page, page_size)


async def update(
    session: AsyncSession,
    note_id: UUID,
    data: NoteUpdate,
) -> Note | None:
    note = await get_by_id(session, note_id)
    if not note:
        return None
    if data.content is not None:
        note.content = data.content
    await session.flush()
    await session.refresh(note)
    return note


async def delete(session: AsyncSession, note_id: UUID) -> bool:
    note = await get_by_id(session, note_id)
    if not note:
        return False
    await session.delete(note)
    await session.flush()
    return True
