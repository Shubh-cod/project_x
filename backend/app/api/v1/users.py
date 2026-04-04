"""User management routes (all users = admin for now)."""
from uuid import UUID
from fastapi import APIRouter, Depends
from app.dependencies import DBSession, CurrentUser
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.common import APIResponse
from app.utils.exceptions import NotFoundError
from sqlalchemy import select
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=APIResponse)
async def list_users(db: DBSession, current_user: CurrentUser):
    result = await db.execute(select(User).order_by(User.email))
    users = result.scalars().all()
    return APIResponse(data=[UserResponse.model_validate(u) for u in users], success=True)


@router.get("/{user_id}", response_model=APIResponse)
async def get_user(user_id: UUID, db: DBSession, current_user: CurrentUser):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("User not found")
    return APIResponse(data=UserResponse.model_validate(user), success=True)


@router.patch("/{user_id}", response_model=APIResponse)
async def update_user(user_id: UUID, data: UserUpdate, db: DBSession, current_user: CurrentUser):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("User not found")
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    await db.flush()
    await db.refresh(user)
    return APIResponse(data=UserResponse.model_validate(user), message="User updated", success=True)
