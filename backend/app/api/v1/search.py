"""Global search across contacts, leads, deals. Cached in Redis."""
from fastapi import APIRouter, Depends, Query
from app.dependencies import DBSession, CurrentUser
from app.schemas.common import APIResponse
from app.services import search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=APIResponse)
async def search(
    db: DBSession,
    current_user: CurrentUser,
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
):
    result = await search_service.search(db, q, user_id=current_user.id, limit=limit, use_cache=True)
    return APIResponse(data=result, success=True)
