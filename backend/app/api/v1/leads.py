"""Lead CRUD, list, convert to contact/deal."""
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from app.dependencies import DBSession, CurrentUser
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse, LeadConvertRequest
from app.schemas.common import APIResponse
from app.utils.exceptions import NotFoundError
from app.services import lead_service

router = APIRouter(prefix="/leads", tags=["leads"])


def _lead_to_response(l):
    return LeadResponse(
        id=l.id,
        title=l.title,
        contact_id=l.contact_id,
        source=l.source,
        status=l.status,
        priority=l.priority,
        assigned_to=l.assigned_to,
        estimated_value=l.estimated_value,
        notes=l.notes,
        status_changed_at=l.status_changed_at,
        created_at=l.created_at,
        updated_at=l.updated_at,
        tags=[t.name for t in getattr(l, "tags", [])],
    )


@router.post("", response_model=APIResponse)
async def create_lead(data: LeadCreate, db: DBSession, current_user: CurrentUser):
    lead = await lead_service.create(db, data, current_user.id)
    return APIResponse(data=_lead_to_response(lead), message="Lead created", success=True)


@router.get("", response_model=APIResponse)
async def list_leads(
    db: DBSession,
    current_user: CurrentUser,
    status: str | None = None,
    contact_id: UUID | None = None,
    assigned_to: UUID | None = None,
    priority: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    from datetime import datetime
    items, total = await lead_service.list_leads(
        db,
        status=status,
        contact_id=contact_id,
        assigned_to=assigned_to,
        priority=priority,
        date_from=datetime.fromisoformat(date_from.replace("Z", "+00:00")) if date_from else None,
        date_to=datetime.fromisoformat(date_to.replace("Z", "+00:00")) if date_to else None,
        page=page,
        page_size=page_size,
    )
    pages = (total + page_size - 1) // page_size if page_size else 0
    return APIResponse(
        data={
            "items": [_lead_to_response(l) for l in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        },
        success=True,
    )


@router.get("/{lead_id}", response_model=APIResponse)
async def get_lead(lead_id: UUID, db: DBSession, current_user: CurrentUser):
    lead = await lead_service.get_by_id(db, lead_id)
    if not lead:
        raise NotFoundError("Lead not found")
    return APIResponse(data=_lead_to_response(lead), success=True)


@router.patch("/{lead_id}", response_model=APIResponse)
async def update_lead(
    lead_id: UUID,
    data: LeadUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    lead = await lead_service.update(db, lead_id, data, current_user.id)
    if not lead:
        raise NotFoundError("Lead not found")
    return APIResponse(data=_lead_to_response(lead), message="Lead updated", success=True)


@router.post("/{lead_id}/convert", response_model=APIResponse)
async def convert_lead(
    lead_id: UUID,
    data: LeadConvertRequest,
    db: DBSession,
    current_user: CurrentUser,
):
    contact, deal = await lead_service.convert_to_contact_and_deal(
        db,
        lead_id,
        create_deal=data.create_deal,
        deal_title=data.deal_title,
        deal_value=data.deal_value,
        user_id=current_user.id,
    )
    from app.schemas.contact import ContactResponse
    result = {"contact": ContactResponse.model_validate(contact)}
    if deal:
        from app.schemas.deal import DealResponse
        result["deal"] = DealResponse.model_validate(deal)
    return APIResponse(data=result, message="Lead converted", success=True)
