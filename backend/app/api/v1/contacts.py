from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from app.dependencies import DBSession, CurrentUser
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse, ContactListFilters
from app.schemas.common import APIResponse, PaginatedResponse
from app.utils.exceptions import NotFoundError
from app.services import contact_service

router = APIRouter(prefix="/contacts", tags=["contacts"])


def _contact_to_response(c):
    return ContactResponse(
        id=c.id,
        name=c.name,
        email=c.email,
        phone=c.phone,
        company=c.company,
        address=c.address,
        source=c.source,
        notes=c.notes,
        assigned_to=c.assigned_to,
        created_at=c.created_at,
        updated_at=c.updated_at,
        tags=[t.name for t in getattr(c, "tags", [])],
    )


@router.post("", response_model=APIResponse)
async def create_contact(data: ContactCreate, db: DBSession, current_user: CurrentUser):
    contact = await contact_service.create(db, data, current_user.id)
    return APIResponse(data=_contact_to_response(contact), message="Contact created", success=True)


@router.get("", response_model=APIResponse)
async def list_contacts(
    db: DBSession,
    current_user: CurrentUser,
    name: str | None = None,
    email: str | None = None,
    tag: str | None = None,
    assigned_to: UUID | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    filters = ContactListFilters(
        name=name,
        email=email,
        tag=tag,
        assigned_to=assigned_to,
        date_from=datetime.fromisoformat(date_from.replace("Z", "+00:00")) if date_from else None,
        date_to=datetime.fromisoformat(date_to.replace("Z", "+00:00")) if date_to else None,
        page=page,
        page_size=page_size,
    )
    items, total = await contact_service.list_contacts(db, filters, user_id=current_user.id)
    pages = (total + page_size - 1) // page_size if page_size else 0
    return APIResponse(
        data={
            "items": [_contact_to_response(c) for c in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        },
        success=True,
    )


@router.get("/{contact_id}", response_model=APIResponse)
async def get_contact(contact_id: UUID, db: DBSession, current_user: CurrentUser):
    contact = await contact_service.get_by_id(db, contact_id, user_id=current_user.id)
    if not contact:
        raise NotFoundError("Contact not found")
    return APIResponse(data=_contact_to_response(contact), success=True)


@router.patch("/{contact_id}", response_model=APIResponse)
async def update_contact(
    contact_id: UUID,
    data: ContactUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    contact = await contact_service.update(db, contact_id, data, current_user.id)
    if not contact:
        raise NotFoundError("Contact not found")
    return APIResponse(data=_contact_to_response(contact), message="Contact updated", success=True)


@router.delete("/{contact_id}", response_model=APIResponse)
async def delete_contact(
    contact_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
    delete_associated: bool = Query(False),
):
    ok = await contact_service.soft_delete(db, contact_id, current_user.id, delete_associated)
    if not ok:
        raise NotFoundError("Contact not found")
    return APIResponse(message="Contact deleted", success=True)
