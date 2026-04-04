"""Task CRUD, overdue query, ARQ reminder scheduling."""
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.utils.pagination import paginate
from app.utils.enums import TaskStatus
from app.services.activity_service import log as activity_log
from app.services.dashboard_service import invalidate_dashboard_cache
from app.schemas.task import TaskCreate, TaskUpdate


async def create(
    session: AsyncSession,
    data: TaskCreate,
    user_id: Optional[UUID] = None,
) -> Task:
    task = Task(
        title=data.title,
        description=data.description,
        due_date=data.due_date,
        priority=data.priority,
        status=data.status,
        linked_to_type=data.linked_to_type,
        linked_to_id=data.linked_to_id,
        assigned_to=data.assigned_to or user_id,  # default to creating user
        owner_id=user_id,
    )
    session.add(task)
    await session.flush()
    await activity_log(session, "task", task.id, "created", user_id, {"title": data.title})
    await invalidate_dashboard_cache(task.assigned_to)
    await session.refresh(task)
    return task


async def get_by_id(session: AsyncSession, task_id: UUID, user_id: Optional[UUID] = None) -> Task | None:
    q = select(Task).where(and_(Task.id == task_id, Task.is_deleted == False))
    if user_id is not None:
        q = q.where(Task.owner_id == user_id)
    result = await session.execute(q)
    return result.scalar_one_or_none()


async def list_tasks(
    session: AsyncSession,
    user_id: Optional[UUID] = None,
    assigned_to: Optional[UUID] = None,
    status: Optional[str] = None,
    linked_to_type: Optional[str] = None,
    linked_to_id: Optional[UUID] = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Task], int]:
    q = (
        select(Task)
        .where(Task.is_deleted == False)
        .order_by(Task.due_date.asc().nullslast(), Task.created_at.desc())
    )
    # ── Data isolation: always filter by owner ──
    if user_id is not None:
        q = q.where(Task.owner_id == user_id)
    if assigned_to:
        q = q.where(Task.assigned_to == assigned_to)
    if status:
        q = q.where(Task.status == status)
    if linked_to_type:
        q = q.where(Task.linked_to_type == linked_to_type)
    if linked_to_id:
        q = q.where(Task.linked_to_id == linked_to_id)
    return await paginate(session, q, page, page_size)


async def overdue_tasks(session: AsyncSession, user_id: Optional[UUID] = None, assigned_to: Optional[UUID] = None) -> list[Task]:
    now = datetime.now(timezone.utc)
    q = (
        select(Task)
        .where(and_(Task.due_date < now, Task.status != TaskStatus.DONE.value, Task.is_deleted == False))
        .order_by(Task.due_date.asc())
    )
    # ── Data isolation: always filter by owner ──
    if user_id is not None:
        q = q.where(Task.owner_id == user_id)
    if assigned_to:
        q = q.where(Task.assigned_to == assigned_to)
    result = await session.execute(q)
    return list(result.scalars().all())


async def update(
    session: AsyncSession,
    task_id: UUID,
    data: TaskUpdate,
    user_id: Optional[UUID] = None,
) -> Task | None:
    task = await get_by_id(session, task_id, user_id=user_id)
    if not task:
        return None
    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    if data.due_date is not None:
        task.due_date = data.due_date
    if data.priority is not None:
        task.priority = data.priority
    if data.status is not None:
        task.status = data.status
    if data.linked_to_type is not None:
        task.linked_to_type = data.linked_to_type
    if data.linked_to_id is not None:
        task.linked_to_id = data.linked_to_id
    if data.assigned_to is not None:
        task.assigned_to = data.assigned_to
    await session.flush()
    await invalidate_dashboard_cache(task.assigned_to)
    await session.refresh(task)
    return task
