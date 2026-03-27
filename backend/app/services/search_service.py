"""Global search across contacts, leads, deals. Redis cache 60s TTL, invalidate on write."""
import hashlib
import json
from typing import Optional

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact
from app.models.lead import Lead
from app.models.deal import Deal
from app.redis.keys import search_cache_key
from app.redis.cache import cache_get_json, cache_set_json

SEARCH_CACHE_TTL = 60


def _query_hash(q: str, limit: int) -> str:
    return hashlib.sha256(f"{q}:{limit}".encode()).hexdigest()


async def search(
    session: AsyncSession,
    query: str,
    limit: int = 20,
    use_cache: bool = True,
) -> dict:
    if not query or not query.strip():
        return {"contacts": [], "leads": [], "deals": []}
    q = query.strip()
    cache_key = search_cache_key(_query_hash(q, limit))
    if use_cache:
        cached = await cache_get_json(cache_key)
        if cached:
            return cached

    like = f"%{q}%"
    contacts_q = (
        select(Contact)
        .where(and_(Contact.is_deleted == False, or_(Contact.name.ilike(like), (Contact.email or "").ilike(like))))
        .limit(limit)
    )
    leads_q = select(Lead).where(Lead.title.ilike(like)).limit(limit)
    deals_q = select(Deal).where(Deal.title.ilike(like)).limit(limit)

    cr = await session.execute(contacts_q)
    lr = await session.execute(leads_q)
    dr = await session.execute(deals_q)
    contacts = [
        {"type": "contact", "id": c.id, "title": c.name, "subtitle": c.email}
        for c in cr.scalars().all()
    ]
    leads = [
        {"type": "lead", "id": l.id, "title": l.title, "subtitle": l.status}
        for l in lr.scalars().all()
    ]
    deals = [
        {"type": "deal", "id": d.id, "title": d.title, "subtitle": d.stage}
        for d in dr.scalars().all()
    ]
    result = {"contacts": contacts, "leads": leads, "deals": deals}
    if use_cache:
        await cache_set_json(cache_key, result, SEARCH_CACHE_TTL)
    return result


async def invalidate_search_cache() -> None:
    """Call on write to contacts/leads/deals. Invalidate all search:* keys."""
    from app.redis.cache import cache_delete_pattern
    await cache_delete_pattern("search:*")
