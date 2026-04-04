"""Dashboard stats: summary, pipeline value, agent performance (SQL aggregations)."""
from datetime import datetime, timezone, timedelta
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact
from app.models.lead import Lead
from app.models.deal import Deal
from app.models.task import Task
from app.models.user import User
from app.utils.enums import UserRole
from app.redis.keys import dashboard_cache_key
from app.redis.cache import cache_get_json, cache_set_json, cache_delete

DASHBOARD_CACHE_TTL = 300  # 5 minutes


async def get_summary_stats(session: AsyncSession, user_id: UUID) -> dict:
    """Summary stats always scoped to the requesting user's data."""
    now = datetime.now(timezone.utc)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_today = start_of_today + timedelta(days=1)

    contacts_q = select(func.count(Contact.id)).where(
        and_(Contact.is_deleted == False, Contact.owner_id == user_id)
    )
    leads_q = select(func.count(Lead.id)).where(
        and_(Lead.status != "lost", Lead.owner_id == user_id)
    )
    deals_won_q = select(func.count(Deal.id)).where(
        and_(Deal.stage == "won", Deal.updated_at >= start_of_month, Deal.owner_id == user_id)
    )
    tasks_today_q = select(func.count(Task.id)).where(
        and_(
            Task.due_date >= start_of_today,
            Task.due_date < end_of_today,
            Task.status != "done",
            Task.owner_id == user_id,
        )
    )

    r1 = await session.execute(contacts_q)
    r2 = await session.execute(leads_q)
    r3 = await session.execute(deals_won_q)
    r4 = await session.execute(tasks_today_q)

    return {
        "total_contacts": r1.scalar_one() or 0,
        "open_leads": r2.scalar_one() or 0,
        "deals_won_this_month": r3.scalar_one() or 0,
        "tasks_due_today": r4.scalar_one() or 0,
    }


async def get_pipeline_by_stage(session: AsyncSession, user_id: UUID) -> list[dict]:
    q = (
        select(Deal.stage, func.count(Deal.id).label("count"), func.coalesce(func.sum(Deal.value), 0).label("total_value"))
        .where(Deal.owner_id == user_id)
        .group_by(Deal.stage)
    )
    result = await session.execute(q)
    return [
        {"stage": r.stage, "count": r.count, "total_value": float(r.total_value)}
        for r in result.all()
    ]


async def get_agent_performance(session: AsyncSession, user_id: UUID, last_n_days: int = 30) -> list[dict]:
    """Show only the requesting user's own performance."""
    since = datetime.now(timezone.utc) - timedelta(days=last_n_days)
    # Deals won by this user
    deals_won_q = (
        select(func.count(Deal.id).label("deals_won"))
        .where(and_(
            Deal.stage == "won",
            Deal.updated_at >= since,
            Deal.owner_id == user_id,
        ))
    )
    # Leads contacted (status != new) by this user
    leads_contacted_q = (
        select(func.count(Lead.id).label("leads_contacted"))
        .where(and_(
            Lead.status != "new",
            Lead.updated_at >= since,
            Lead.owner_id == user_id,
        ))
    )
    dw_result = await session.execute(deals_won_q)
    lc_result = await session.execute(leads_contacted_q)
    deals_won = dw_result.scalar_one() or 0
    leads_contacted = lc_result.scalar_one() or 0

    # Fetch user info
    user_q = select(User).where(User.id == user_id)
    user_result = await session.execute(user_q)
    user = user_result.scalar_one_or_none()

    return [
        {
            "user_id": str(user_id),
            "full_name": user.full_name if user else "Unknown",
            "deals_won": deals_won,
            "leads_contacted": leads_contacted,
        }
    ]


async def get_dashboard(session: AsyncSession, user_id: UUID, role: UserRole) -> dict:
    cache_key = dashboard_cache_key(user_id)
    cached = await cache_get_json(cache_key)
    if cached:
        return cached
    summary = await get_summary_stats(session, user_id)
    pipeline = await get_pipeline_by_stage(session, user_id)
    agents = await get_agent_performance(session, user_id)
    data = {
        "summary": summary,
        "pipeline_by_stage": pipeline,
        "agent_performance": agents,
    }
    await cache_set_json(cache_key, data, DASHBOARD_CACHE_TTL)
    return data


async def invalidate_dashboard_cache(user_id: UUID | None = None) -> None:
    if user_id:
        await cache_delete(dashboard_cache_key(user_id))
    # Note: If global stats change, we might need to invalidate all dashboard caches.
    # For now, let's just invalidate the specific user's cache and a global one if it exists.
    # In a production app, we might use cache tags or just invalidate all with a pattern.
    from app.redis.cache import cache_delete_pattern
    await cache_delete_pattern("dashboard:*")
