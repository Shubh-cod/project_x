"""Activity feed per entity and global."""
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from app.dependencies import DBSession, CurrentUser
from app.schemas.activity import ActivityResponse
from app.schemas.common import APIResponse
from app.services import activity_service

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("/entity/{entity_type}/{entity_id}", response_model=APIResponse)
async def list_entity_activities(
    entity_type: str,
    entity_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = await activity_service.list_by_entity(db, entity_type, entity_id, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size if page_size else 0
    return APIResponse(
        data={
            "items": [ActivityResponse.model_validate(a) for a in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        },
        success=True,
    )


@router.get("", response_model=APIResponse)
async def list_global_activities(
    db: DBSession,
    current_user: CurrentUser,
    user_id: UUID | None = None,
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    from datetime import datetime
    items, total = await activity_service.list_global(
        db,
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        date_from=datetime.fromisoformat(date_from.replace("Z", "+00:00")) if date_from else None,
        date_to=datetime.fromisoformat(date_to.replace("Z", "+00:00")) if date_to else None,
        page=page,
        page_size=page_size,
    )
    pages = (total + page_size - 1) // page_size if page_size else 0
    return APIResponse(
        data={
            "items": [ActivityResponse.model_validate(a) for a in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        },
        success=True,
    )
