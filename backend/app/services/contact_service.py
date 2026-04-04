"""Contact CRUD, search, filter, soft delete, activity logging."""
from uuid import UUID
from datetime import datetime
from typing import Optional

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.contact import Contact
from app.models.tag import Tag, contact_tags
from app.utils.pagination import paginate
from app.utils.exceptions import NotFoundError
from app.services.activity_service import log as activity_log
from app.services.search_service import invalidate_search_cache
from app.services.dashboard_service import invalidate_dashboard_cache
from app.schemas.contact import ContactCreate, ContactUpdate, ContactListFilters


async def create(
    session: AsyncSession,
    data: ContactCreate,
    user_id: Optional[UUID] = None,
) -> Contact:
    contact = Contact(
        name=data.name,
        email=data.email,
        phone=data.phone,
        company=data.company,
        address=data.address,
        source=data.source,
        notes=data.notes,
        assigned_to=data.assigned_to,
    )
    session.add(contact)
    await session.flush()
    if data.tags:
        await _set_contact_tags(session, contact.id, data.tags)
    await activity_log(session, "contact", contact.id, "created", user_id, {"entity_name": contact.name})
    await invalidate_search_cache()
    await invalidate_dashboard_cache(contact.assigned_to)
    await session.refresh(contact)
    return contact


async def get_by_id(session: AsyncSession, contact_id: UUID) -> Contact | None:
    result = await session.execute(
        select(Contact)
        .where(and_(Contact.id == contact_id, Contact.is_deleted == False))
        .options(selectinload(Contact.tags))
    )
    return result.scalar_one_or_none()


async def list_contacts(
    session: AsyncSession,
    filters: ContactListFilters,
) -> tuple[list[Contact], int]:
    q = (
        select(Contact)
        .where(Contact.is_deleted == False)
        .options(selectinload(Contact.tags))
    )
    if filters.name:
        q = q.where(Contact.name.ilike(f"%{filters.name}%"))
    if filters.email:
        q = q.where(Contact.email.ilike(f"%{filters.email}%"))
    if filters.assigned_to:
        q = q.where(Contact.assigned_to == filters.assigned_to)
    if filters.date_from:
        q = q.where(Contact.created_at >= filters.date_from)
    if filters.date_to:
        q = q.where(Contact.created_at <= filters.date_to)
    if filters.tag:
        sub = select(contact_tags.c.contact_id).select_from(contact_tags).join(Tag, contact_tags.c.tag_id == Tag.id).where(Tag.name == filters.tag)
        q = q.where(Contact.id.in_(sub))
    q = q.order_by(Contact.created_at.desc())
    return await paginate(session, q, filters.page, filters.page_size)


async def update(
    session: AsyncSession,
    contact_id: UUID,
    data: ContactUpdate,
    user_id: Optional[UUID] = None,
) -> Contact | None:
    contact = await get_by_id(session, contact_id)
    if not contact:
        return None
    if data.name is not None:
        contact.name = data.name
    if data.email is not None:
        contact.email = data.email
    if data.phone is not None:
        contact.phone = data.phone
    if data.company is not None:
        contact.company = data.company
    if data.address is not None:
        contact.address = data.address
    if data.source is not None:
        contact.source = data.source
    if data.notes is not None:
        contact.notes = data.notes
    if data.assigned_to is not None:
        contact.assigned_to = data.assigned_to
    if data.tags is not None:
        await _set_contact_tags(session, contact.id, data.tags)
    await activity_log(session, "contact", contact.id, "updated", user_id, {"entity_name": contact.name})
    await invalidate_search_cache()
    await invalidate_dashboard_cache(contact.assigned_to)
    await session.flush()
    await session.refresh(contact)
    return contact


async def soft_delete(session: AsyncSession, contact_id: UUID, user_id: Optional[UUID] = None) -> bool:
    contact = await get_by_id(session, contact_id)
    if not contact:
        return False
    contact.is_deleted = True
    await invalidate_search_cache()
    await invalidate_dashboard_cache(contact.assigned_to)
    await session.flush()
    return True


async def _set_contact_tags(session: AsyncSession, contact_id: UUID, tag_names: list[str]) -> None:
    await session.execute(contact_tags.delete().where(contact_tags.c.contact_id == contact_id))
    for name in tag_names:
        r = await session.execute(select(Tag).where(Tag.name == name.strip()))
        tag = r.scalar_one_or_none()
        if tag:
            await session.execute(contact_tags.insert().values(contact_id=contact_id, tag_id=tag.id))
    await session.flush()
