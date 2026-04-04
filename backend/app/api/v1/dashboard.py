"""Dashboard summary, pipeline, agent performance."""
from fastapi import APIRouter, Depends
from app.dependencies import DBSession, CurrentUser
from app.schemas.common import APIResponse
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=APIResponse)
async def get_dashboard(db: DBSession, current_user: CurrentUser):
    data = await dashboard_service.get_dashboard(db, current_user.id, current_user.role)
    return APIResponse(data=data, success=True)
