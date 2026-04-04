"""Lead CRUD, status pipeline, conversion to contact/deal, activity logging."""
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.lead import Lead
from app.models.contact import Contact
from app.models.deal import Deal
from app.models.tag import Tag, lead_tags
from app.utils.enums import LeadStatus
from app.utils.exceptions import NotFoundError
from app.utils.pagination import paginate
from app.services.activity_service import log as activity_log
from app.services.contact_service import get_by_id as get_contact_by_id
from app.services.search_service import invalidate_search_cache
from app.services.dashboard_service import invalidate_dashboard_cache
from app.schemas.lead import LeadCreate, LeadUpdate


async def create(
    session: AsyncSession,
    data: LeadCreate,
    user_id: Optional[UUID] = None,
) -> Lead:
    lead = Lead(
        title=data.title,
        contact_id=data.contact_id,
        source=data.source,
        status=data.status,
        priority=data.priority,
        assigned_to=data.assigned_to,
        estimated_value=data.estimated_value,
        notes=data.notes,
        status_changed_at=datetime.now(timezone.utc),
        owner_id=user_id,
    )
    session.add(lead)
    await session.flush()
    if data.tags:
        await _set_lead_tags(session, lead.id, data.tags)
    await activity_log(session, "lead", lead.id, "created", user_id, {"entity_name": lead.title})
    await invalidate_search_cache()
    await invalidate_dashboard_cache(lead.assigned_to)
    await session.refresh(lead)
    # Fire automation triggers (non-fatal)
    try:
        from app.services import automation_service
        await automation_service.execute_trigger(session, "lead_created", {
            "lead_id": lead.id,
            "lead_title": lead.title,
            "contact_id": lead.contact_id,
            "user_id": user_id,
            "entity_name": lead.title,
        })
    except Exception as e:
        import logging
        logging.getLogger("novacrm.automation").warning(f"Lead automation trigger failed: {e}")
    return lead


async def get_by_id(session: AsyncSession, lead_id: UUID, user_id: Optional[UUID] = None) -> Lead | None:
    q = select(Lead).where(Lead.id == lead_id).options(selectinload(Lead.tags))
    if user_id is not None:
        q = q.where(Lead.owner_id == user_id)
    result = await session.execute(q)
    return result.scalar_one_or_none()


async def list_leads(
    session: AsyncSession,
    user_id: Optional[UUID] = None,
    status: Optional[str] = None,
    contact_id: Optional[UUID] = None,
    assigned_to: Optional[UUID] = None,
    priority: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Lead], int]:
    q = select(Lead).options(selectinload(Lead.tags)).order_by(Lead.created_at.desc())
    # ── Data isolation: always filter by owner ──
    if user_id is not None:
        q = q.where(Lead.owner_id == user_id)
    if status:
        q = q.where(Lead.status == status)
    if contact_id:
        q = q.where(Lead.contact_id == contact_id)
    if assigned_to:
        q = q.where(Lead.assigned_to == assigned_to)
    if priority:
        q = q.where(Lead.priority == priority)
    if date_from:
        q = q.where(Lead.created_at >= date_from)
    if date_to:
        q = q.where(Lead.created_at <= date_to)
    return await paginate(session, q, page, page_size)


async def update(
    session: AsyncSession,
    lead_id: UUID,
    data: LeadUpdate,
    user_id: Optional[UUID] = None,
) -> Lead | None:
    lead = await get_by_id(session, lead_id, user_id=user_id)
    if not lead:
        return None
    old_status = lead.status
    if data.title is not None:
        lead.title = data.title
    if data.contact_id is not None:
        lead.contact_id = data.contact_id
    if data.source is not None:
        lead.source = data.source
    if data.status is not None:
        lead.status = data.status
        lead.status_changed_at = datetime.now(timezone.utc)
    if data.priority is not None:
        lead.priority = data.priority
    if data.assigned_to is not None:
        lead.assigned_to = data.assigned_to
    if data.estimated_value is not None:
        lead.estimated_value = data.estimated_value
    if data.notes is not None:
        lead.notes = data.notes
    if data.tags is not None:
        await _set_lead_tags(session, lead.id, data.tags)
    await invalidate_search_cache()
    await invalidate_dashboard_cache(lead.assigned_to)
    await session.flush()
    if data.status is not None and data.status != old_status:
        await activity_log(session, "lead", lead.id, "status_changed", user_id, {"old": old_status, "new": data.status, "entity_name": lead.title})
    else:
        await activity_log(session, "lead", lead.id, "updated", user_id, {"entity_name": lead.title})
    await session.refresh(lead)
    return lead


async def convert_to_contact_and_deal(
    session: AsyncSession,
    lead_id: UUID,
    create_deal: bool = False,
    deal_title: Optional[str] = None,
    deal_value: Optional[float] = None,
    user_id: Optional[UUID] = None,
) -> tuple[Contact, Optional[Deal]]:
    lead = await get_by_id(session, lead_id, user_id=user_id)
    if not lead:
        raise NotFoundError("Lead not found")
    contact = await get_contact_by_id(session, lead.contact_id, user_id=user_id)
    if not contact:
        raise NotFoundError("Contact not found")
    deal = None
    if create_deal and deal_title:
        deal = Deal(
            title=deal_title,
            contact_id=lead.contact_id,
            lead_id=lead.id,
            stage="prospect",
            value=deal_value or 0,
            assigned_to=lead.assigned_to,
            owner_id=user_id,
        )
        session.add(deal)
        await session.flush()
        await activity_log(session, "deal", deal.id, "created", user_id)
    await activity_log(session, "lead", lead.id, "converted", user_id, {"contact_id": str(contact.id), "deal_id": str(deal.id) if deal else None})
    await invalidate_dashboard_cache(lead.assigned_to)
    await session.flush()
    return contact, deal


async def _set_lead_tags(session: AsyncSession, lead_id: UUID, tag_names: list[str]) -> None:
    await session.execute(lead_tags.delete().where(lead_tags.c.lead_id == lead_id))
    for name in tag_names:
        r = await session.execute(select(Tag).where(Tag.name == name.strip()))
        tag = r.scalar_one_or_none()
        if tag:
            await session.execute(lead_tags.insert().values(lead_id=lead_id, tag_id=tag.id))
    await session.flush()
