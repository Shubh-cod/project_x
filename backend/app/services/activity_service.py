"""Activity logging helper - called by other services to log entity events."""
from uuid import UUID
from typing import Any, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.utils.enums import ActivityAction
from app.utils.pagination import paginate


async def log(
    session: AsyncSession,
    entity_type: str,
    entity_id: UUID,
    action: str,
    user_id: Optional[UUID] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> Activity:
    """Create an activity record. Actions: created, updated, status_changed, assigned, note_added, converted."""
    activity = Activity(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        user_id=user_id,
        metadata_=metadata,
    )
    session.add(activity)
    await session.flush()
    return activity


async def list_by_entity(
    session: AsyncSession,
    entity_type: str,
    entity_id: UUID,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Activity], int]:
    q = (
        select(Activity)
        .where(Activity.entity_type == entity_type, Activity.entity_id == entity_id)
        .order_by(Activity.created_at.desc())
    )
    return await paginate(session, q, page, page_size)


async def list_global(
    session: AsyncSession,
    user_id: Optional[UUID] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[UUID] = None,
    date_from: Optional[Any] = None,
    date_to: Optional[Any] = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Activity], int]:
    q = select(Activity).order_by(Activity.created_at.desc())
    if user_id:
        q = q.where(Activity.user_id == user_id)
    if entity_type:
        q = q.where(Activity.entity_type == entity_type)
    if entity_id:
        q = q.where(Activity.entity_id == entity_id)
    if date_from:
        q = q.where(Activity.created_at >= date_from)
    if date_to:
        q = q.where(Activity.created_at <= date_to)
    return await paginate(session, q, page, page_size)
