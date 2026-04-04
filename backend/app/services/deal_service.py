"""Deal CRUD, pipeline view, won/lost reason, activity log."""
from uuid import UUID
from typing import Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal
from app.utils.pagination import paginate
from app.services.activity_service import log as activity_log
from app.services.search_service import invalidate_search_cache
from app.services.dashboard_service import invalidate_dashboard_cache
from app.schemas.deal import DealCreate, DealUpdate


async def create(
    session: AsyncSession,
    data: DealCreate,
    user_id: Optional[UUID] = None,
) -> Deal:
    deal = Deal(
        title=data.title,
        contact_id=data.contact_id,
        lead_id=data.lead_id,
        stage=data.stage,
        value=data.value,
        currency=data.currency,
        close_date=data.close_date,
        probability=data.probability,
        assigned_to=data.assigned_to,
        notes=data.notes,
    )
    session.add(deal)
    await session.flush()
    await activity_log(session, "deal", deal.id, "created", user_id, {"entity_name": deal.title})
    await invalidate_search_cache()
    await invalidate_dashboard_cache(deal.assigned_to)
    await session.refresh(deal)
    return deal


async def get_by_id(session: AsyncSession, deal_id: UUID) -> Deal | None:
    result = await session.execute(select(Deal).where(Deal.id == deal_id))
    return result.scalar_one_or_none()


async def list_deals(
    session: AsyncSession,
    stage: Optional[str] = None,
    assigned_to: Optional[UUID] = None,
    contact_id: Optional[UUID] = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Deal], int]:
    q = select(Deal).order_by(Deal.updated_at.desc())
    if stage:
        q = q.where(Deal.stage == stage)
    if assigned_to:
        q = q.where(Deal.assigned_to == assigned_to)
    if contact_id:
        q = q.where(Deal.contact_id == contact_id)
    return await paginate(session, q, page, page_size)


async def update(
    session: AsyncSession,
    deal_id: UUID,
    data: DealUpdate,
    user_id: Optional[UUID] = None,
) -> Deal | None:
    deal = await get_by_id(session, deal_id)
    if not deal:
        return None
    old_stage = deal.stage
    if data.title is not None:
        deal.title = data.title
    if data.contact_id is not None:
        deal.contact_id = data.contact_id
    if data.lead_id is not None:
        deal.lead_id = data.lead_id
    if data.stage is not None:
        deal.stage = data.stage
    if data.value is not None:
        deal.value = data.value
    if data.currency is not None:
        deal.currency = data.currency
    if data.close_date is not None:
        deal.close_date = data.close_date
    if data.probability is not None:
        deal.probability = data.probability
    if data.assigned_to is not None:
        deal.assigned_to = data.assigned_to
    if data.notes is not None:
        deal.notes = data.notes
    if data.won_reason is not None:
        deal.won_reason = data.won_reason
    if data.lost_reason is not None:
        deal.lost_reason = data.lost_reason
    await invalidate_search_cache()
    await invalidate_dashboard_cache(deal.assigned_to)
    await session.flush()
    if data.stage is not None and data.stage != old_stage:
        await activity_log(session, "deal", deal.id, "status_changed", user_id, {"old": old_stage, "new": data.stage, "entity_name": deal.title})
    else:
        await activity_log(session, "deal", deal.id, "updated", user_id, {"entity_name": deal.title})
    await session.refresh(deal)
    # Fire deal_stale automation if deal hasn't progressed
    try:
        from datetime import datetime, timezone, timedelta
        if (
            deal.stage not in ("won", "lost")
            and deal.updated_at
            and deal.updated_at < datetime.now(timezone.utc) - timedelta(days=5)
        ):
            from app.services import automation_service
            await automation_service.execute_trigger(session, "deal_stale", {
                "deal_id": deal.id,
                "deal_title": deal.title,
                "contact_id": deal.contact_id,
                "user_id": user_id,
                "entity_name": deal.title,
            })
    except Exception as e:
        import logging
        logging.getLogger("novacrm.automation").warning(f"Deal automation trigger failed: {e}")
    return deal


async def pipeline_by_stage(session: AsyncSession) -> list[dict]:
    """Group deals by stage with count and total value."""
    q = (
        select(Deal.stage, func.count(Deal.id).label("count"), func.coalesce(func.sum(Deal.value), 0).label("total_value"))
        .group_by(Deal.stage)
    )
    result = await session.execute(q)
    rows = result.all()
    return [{"stage": r.stage, "count": r.count, "total_value": float(r.total_value)} for r in rows]
