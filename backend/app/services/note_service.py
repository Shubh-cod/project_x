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
        owner_id=user_id,
    )
    session.add(note)
    await session.flush()
    # Fetch entity name for activity log
    entity_name = None
    if data.entity_type == "contact":
        from app.models.contact import Contact
        r = await session.execute(select(Contact).where(Contact.id == data.entity_id))
        entity_name = getattr(r.scalar_one_or_none(), "name", None)
    elif data.entity_type == "lead":
        from app.models.lead import Lead
        r = await session.execute(select(Lead).where(Lead.id == data.entity_id))
        entity_name = getattr(r.scalar_one_or_none(), "title", None)
    elif data.entity_type == "deal":
        from app.models.deal import Deal
        r = await session.execute(select(Deal).where(Deal.id == data.entity_id))
        entity_name = getattr(r.scalar_one_or_none(), "title", None)

    await activity_log(session, data.entity_type, data.entity_id, "note_added", user_id, {"note_id": str(note.id), "entity_name": entity_name})
    await session.refresh(note)
    return note


async def get_by_id(session: AsyncSession, note_id: UUID, user_id: Optional[UUID] = None) -> Note | None:
    q = select(Note).where(Note.id == note_id)
    if user_id is not None:
        q = q.where(Note.owner_id == user_id)
    result = await session.execute(q)
    return result.scalar_one_or_none()


async def list_by_entity(
    session: AsyncSession,
    entity_type: str,
    entity_id: UUID,
    user_id: Optional[UUID] = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Note], int]:
    q = (
        select(Note)
        .where(Note.entity_type == entity_type, Note.entity_id == entity_id)
        .order_by(Note.created_at.desc())
    )
    # ── Data isolation: only show notes owned by user ──
    if user_id is not None:
        q = q.where(Note.owner_id == user_id)
    return await paginate(session, q, page, page_size)


async def update(
    session: AsyncSession,
    note_id: UUID,
    data: NoteUpdate,
    user_id: Optional[UUID] = None,
) -> Note | None:
    note = await get_by_id(session, note_id, user_id=user_id)
    if not note:
        return None
    if data.content is not None:
        note.content = data.content
    await session.flush()
    await session.refresh(note)
    return note


async def delete(session: AsyncSession, note_id: UUID, user_id: Optional[UUID] = None) -> bool:
    note = await get_by_id(session, note_id, user_id=user_id)
    if not note:
        return False
    await session.delete(note)
    await session.flush()
    return True
