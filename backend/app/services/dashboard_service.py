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


async def get_summary_stats(session: AsyncSession, user_id: UUID | None = None, role: UserRole | None = None) -> dict:
    now = datetime.now(timezone.utc)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_today = start_of_today + timedelta(days=1)

    contacts_q = select(func.count(Contact.id)).where(Contact.is_deleted == False)
    leads_q = select(func.count(Lead.id)).where(Lead.status != "lost")
    deals_won_q = select(func.count(Deal.id)).where(
        and_(Deal.stage == "won", Deal.updated_at >= start_of_month)
    )
    tasks_today_q = select(func.count(Task.id)).where(
        and_(
            Task.due_date >= start_of_today,
            Task.due_date < end_of_today,
            Task.status != "done",
        )
    )

    # Filtering for non-admins
    if role and role != UserRole.admin:
        contacts_q = contacts_q.where(Contact.assigned_to == user_id)
        leads_q = leads_q.where(Lead.assigned_to == user_id)
        deals_won_q = deals_won_q.where(Deal.assigned_to == user_id)
        tasks_today_q = tasks_today_q.where(Task.assigned_to == user_id)

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


async def get_pipeline_by_stage(session: AsyncSession, user_id: UUID | None = None, role: UserRole | None = None) -> list[dict]:
    q = (
        select(Deal.stage, func.count(Deal.id).label("count"), func.coalesce(func.sum(Deal.value), 0).label("total_value"))
        .group_by(Deal.stage)
    )
    if role and role != UserRole.admin:
        q = q.where(Deal.assigned_to == user_id)
        
    result = await session.execute(q)
    return [
        {"stage": r.stage, "count": r.count, "total_value": float(r.total_value)}
        for r in result.all()
    ]


async def get_agent_performance(session: AsyncSession, last_n_days: int = 30) -> list[dict]:
    since = datetime.now(timezone.utc) - timedelta(days=last_n_days)
    # Deals won per user
    deals_won_q = (
        select(Deal.assigned_to, func.count(Deal.id).label("deals_won"))
        .where(and_(Deal.stage == "won", Deal.updated_at >= since, Deal.assigned_to.isnot(None)))
        .group_by(Deal.assigned_to)
    )
    # Leads contacted (status != new) per user - approximate "contacted" as status not new
    leads_contacted_q = (
        select(Lead.assigned_to, func.count(Lead.id).label("leads_contacted"))
        .where(and_(Lead.status != "new", Lead.updated_at >= since, Lead.assigned_to.isnot(None)))
        .group_by(Lead.assigned_to)
    )
    dw_result = await session.execute(deals_won_q)
    lc_result = await session.execute(leads_contacted_q)
    dw_map = {str(r.assigned_to): r.deals_won for r in dw_result.all()}
    lc_map = {str(r.assigned_to): r.leads_contacted for r in lc_result.all()}
    all_user_ids = set(dw_map.keys()) | set(lc_map.keys())
    if not all_user_ids:
        return []
    users_q = select(User).where(User.id.in_([UUID(uid) for uid in all_user_ids]))
    users_result = await session.execute(users_q)
    users = {str(u.id): u for u in users_result.scalars().all()}
    return [
        {
            "user_id": uid,
            "full_name": users[uid].full_name if uid in users else "Unknown",
            "deals_won": dw_map.get(uid, 0),
            "leads_contacted": lc_map.get(uid, 0),
        }
        for uid in sorted(all_user_ids)
    ]


async def get_dashboard(session: AsyncSession, user_id: UUID, role: UserRole) -> dict:
    cache_key = dashboard_cache_key(user_id)
    cached = await cache_get_json(cache_key)
    if cached:
        return cached
    summary = await get_summary_stats(session, user_id, role)
    pipeline = await get_pipeline_by_stage(session, user_id, role)
    agents = await get_agent_performance(session)
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
