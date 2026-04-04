"""Email activity log - log outbound emails to contacts."""
from uuid import UUID
from fastapi import APIRouter, Depends
from app.dependencies import DBSession, CurrentUser
from app.schemas.email_log import EmailLogCreate, EmailLogResponse
from app.schemas.common import APIResponse
from app.utils.exceptions import NotFoundError
from app.services import email_log_service

router = APIRouter(prefix="/email-logs", tags=["email-logs"])


@router.post("", response_model=APIResponse)
async def create_email_log(data: EmailLogCreate, db: DBSession, current_user: CurrentUser):
    log_entry = await email_log_service.create(db, data, current_user.id)
    return APIResponse(data=EmailLogResponse.model_validate(log_entry), message="Email logged", success=True)


@router.get("/contact/{contact_id}", response_model=APIResponse)
async def list_by_contact(
    contact_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
    limit: int = 50,
):
    logs = await email_log_service.list_by_contact(db, contact_id, user_id=current_user.id, limit=limit)
    return APIResponse(data=[EmailLogResponse.model_validate(l) for l in logs], success=True)


@router.get("/{log_id}", response_model=APIResponse)
async def get_email_log(log_id: UUID, db: DBSession, current_user: CurrentUser):
    log_entry = await email_log_service.get_by_id(db, log_id, user_id=current_user.id)
    if not log_entry:
        raise NotFoundError("Email log not found")
    return APIResponse(data=EmailLogResponse.model_validate(log_entry), success=True)
