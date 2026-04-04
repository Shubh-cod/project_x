"""Notes attached to contact/lead/deal."""
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from app.dependencies import DBSession, CurrentUser
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse
from app.schemas.common import APIResponse
from app.utils.exceptions import NotFoundError
from app.services import note_service

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=APIResponse)
async def create_note(data: NoteCreate, db: DBSession, current_user: CurrentUser):
    note = await note_service.create(db, data, current_user.id)
    return APIResponse(data=NoteResponse.model_validate(note), message="Note added", success=True)


@router.get("", response_model=APIResponse)
async def list_notes_by_entity(
    entity_type: str,
    entity_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = await note_service.list_by_entity(
        db, entity_type, entity_id, user_id=current_user.id, page=page, page_size=page_size,
    )
    pages = (total + page_size - 1) // page_size if page_size else 0
    return APIResponse(
        data={
            "items": [NoteResponse.model_validate(n) for n in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        },
        success=True,
    )


@router.get("/{note_id}", response_model=APIResponse)
async def get_note(note_id: UUID, db: DBSession, current_user: CurrentUser):
    note = await note_service.get_by_id(db, note_id, user_id=current_user.id)
    if not note:
        raise NotFoundError("Note not found")
    return APIResponse(data=NoteResponse.model_validate(note), success=True)


@router.patch("/{note_id}", response_model=APIResponse)
async def update_note(
    note_id: UUID,
    data: NoteUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    note = await note_service.update(db, note_id, data, user_id=current_user.id)
    if not note:
        raise NotFoundError("Note not found")
    return APIResponse(data=NoteResponse.model_validate(note), message="Note updated", success=True)


@router.delete("/{note_id}", response_model=APIResponse)
async def delete_note(note_id: UUID, db: DBSession, current_user: CurrentUser):
    ok = await note_service.delete(db, note_id, user_id=current_user.id)
    if not ok:
        raise NotFoundError("Note not found")
    return APIResponse(message="Note deleted", success=True)
