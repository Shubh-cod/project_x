"""Deal CRUD, list, pipeline view."""
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from app.dependencies import DBSession, CurrentUser
from app.schemas.deal import DealCreate, DealUpdate, DealResponse, DealPipelineResponse
from app.schemas.common import APIResponse
from app.utils.exceptions import NotFoundError
from app.services import deal_service

router = APIRouter(prefix="/deals", tags=["deals"])


@router.post("", response_model=APIResponse)
async def create_deal(data: DealCreate, db: DBSession, current_user: CurrentUser):
    deal = await deal_service.create(db, data, current_user.id)
    return APIResponse(data=DealResponse.model_validate(deal), message="Deal created", success=True)


@router.get("", response_model=APIResponse)
async def list_deals(
    db: DBSession,
    current_user: CurrentUser,
    stage: str | None = None,
    assigned_to: UUID | None = None,
    contact_id: UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = await deal_service.list_deals(
        db, user_id=current_user.id, stage=stage, assigned_to=assigned_to,
        contact_id=contact_id, page=page, page_size=page_size,
    )
    pages = (total + page_size - 1) // page_size if page_size else 0
    return APIResponse(
        data={
            "items": [DealResponse.model_validate(d) for d in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        },
        success=True,
    )


@router.get("/pipeline", response_model=APIResponse)
async def pipeline(db: DBSession, current_user: CurrentUser):
    stages = await deal_service.pipeline_by_stage(db, user_id=current_user.id)
    return APIResponse(data={"stages": stages}, success=True)


@router.get("/{deal_id}", response_model=APIResponse)
async def get_deal(deal_id: UUID, db: DBSession, current_user: CurrentUser):
    deal = await deal_service.get_by_id(db, deal_id, user_id=current_user.id)
    if not deal:
        raise NotFoundError("Deal not found")
    return APIResponse(data=DealResponse.model_validate(deal), success=True)


@router.patch("/{deal_id}", response_model=APIResponse)
async def update_deal(
    deal_id: UUID,
    data: DealUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    deal = await deal_service.update(db, deal_id, data, current_user.id)
    if not deal:
        raise NotFoundError("Deal not found")
    return APIResponse(data=DealResponse.model_validate(deal), message="Deal updated", success=True)
