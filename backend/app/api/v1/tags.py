"""Tag CRUD, attach/detach on contacts and leads."""
from uuid import UUID
from fastapi import APIRouter, Depends
from app.dependencies import DBSession, CurrentUser
from app.schemas.tag import TagCreate, TagUpdate, TagResponse
from app.schemas.common import APIResponse
from app.utils.exceptions import NotFoundError
from app.services import tag_service

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("", response_model=APIResponse)
async def create_tag(data: TagCreate, db: DBSession, current_user: CurrentUser):
    tag = await tag_service.create(db, data)
    return APIResponse(data=TagResponse.model_validate(tag), message="Tag created", success=True)


@router.get("", response_model=APIResponse)
async def list_tags(db: DBSession, current_user: CurrentUser):
    tags = await tag_service.list_all(db)
    return APIResponse(data=[TagResponse.model_validate(t) for t in tags], success=True)


@router.get("/{tag_id}", response_model=APIResponse)
async def get_tag(tag_id: UUID, db: DBSession, current_user: CurrentUser):
    tag = await tag_service.get_by_id(db, tag_id)
    if not tag:
        raise NotFoundError("Tag not found")
    return APIResponse(data=TagResponse.model_validate(tag), success=True)


@router.patch("/{tag_id}", response_model=APIResponse)
async def update_tag(
    tag_id: UUID,
    data: TagUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    tag = await tag_service.update(db, tag_id, data)
    if not tag:
        raise NotFoundError("Tag not found")
    return APIResponse(data=TagResponse.model_validate(tag), message="Tag updated", success=True)


@router.delete("/{tag_id}", response_model=APIResponse)
async def delete_tag(tag_id: UUID, db: DBSession, current_user: CurrentUser):
    ok = await tag_service.delete(db, tag_id)
    if not ok:
        raise NotFoundError("Tag not found")
    return APIResponse(message="Tag deleted", success=True)
