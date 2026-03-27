"""Task CRUD, list, overdue."""
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from app.dependencies import DBSession, CurrentUser
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.schemas.common import APIResponse
from app.utils.exceptions import NotFoundError
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=APIResponse)
async def create_task(data: TaskCreate, db: DBSession, current_user: CurrentUser):
    task = await task_service.create(db, data, current_user.id)
    return APIResponse(data=TaskResponse.model_validate(task), message="Task created", success=True)


@router.get("", response_model=APIResponse)
async def list_tasks(
    db: DBSession,
    current_user: CurrentUser,
    assigned_to: UUID | None = None,
    status: str | None = None,
    linked_to_type: str | None = None,
    linked_to_id: UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = await task_service.list_tasks(
        db,
        assigned_to=assigned_to or current_user.id,
        status=status,
        linked_to_type=linked_to_type,
        linked_to_id=linked_to_id,
        page=page,
        page_size=page_size,
    )
    pages = (total + page_size - 1) // page_size if page_size else 0
    return APIResponse(
        data={
            "items": [TaskResponse.model_validate(t) for t in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        },
        success=True,
    )


@router.get("/overdue", response_model=APIResponse)
async def overdue_tasks(db: DBSession, current_user: CurrentUser):
    tasks = await task_service.overdue_tasks(db, assigned_to=current_user.id)
    return APIResponse(data=[TaskResponse.model_validate(t) for t in tasks], success=True)


@router.get("/{task_id}", response_model=APIResponse)
async def get_task(task_id: UUID, db: DBSession, current_user: CurrentUser):
    task = await task_service.get_by_id(db, task_id)
    if not task:
        raise NotFoundError("Task not found")
    return APIResponse(data=TaskResponse.model_validate(task), success=True)


@router.patch("/{task_id}", response_model=APIResponse)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    task = await task_service.update(db, task_id, data, current_user.id)
    if not task:
        raise NotFoundError("Task not found")
    return APIResponse(data=TaskResponse.model_validate(task), message="Task updated", success=True)
