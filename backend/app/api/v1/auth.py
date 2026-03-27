"""Auth routes: register, login, logout, refresh, profile, change password."""
from fastapi import APIRouter
from app.dependencies import DBSession, get_current_user, CurrentUser
from app.schemas.auth import LoginRequest, RegisterRequest, RefreshRequest, TokenResponse, ChangePasswordRequest
from app.schemas.user import UserResponse, UserProfileUpdate
from app.schemas.common import APIResponse, MessageResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=APIResponse)
async def register(data: RegisterRequest, db: DBSession):
    user = await auth_service.register(db, data)
    return APIResponse(data=UserResponse.model_validate(user), message="Registered successfully", success=True)


@router.post("/login", response_model=APIResponse)
async def login(data: LoginRequest, db: DBSession):
    user, tokens = await auth_service.login(db, data)
    return APIResponse(
        data={"user": UserResponse.model_validate(user), "tokens": tokens.model_dump()},
        message="Login successful",
        success=True,
    )


@router.post("/logout", response_model=APIResponse)
async def logout(current_user: CurrentUser):
    await auth_service.logout(current_user.id)
    return APIResponse(message="Logged out", success=True)


@router.post("/refresh", response_model=APIResponse)
async def refresh(data: RefreshRequest, db: DBSession):
    tokens = await auth_service.refresh_tokens(db, data.refresh_token)
    return APIResponse(data=tokens.model_dump(), message="Token refreshed", success=True)


@router.get("/me", response_model=APIResponse)
async def get_me(current_user: CurrentUser, db: DBSession):
    user = await auth_service.get_profile(db, current_user.id)
    if not user:
        return APIResponse(data=None, message="User not found", success=False)
    return APIResponse(data=UserResponse.model_validate(user), success=True)


@router.patch("/me", response_model=APIResponse)
async def update_me(data: UserProfileUpdate, current_user: CurrentUser, db: DBSession):
    user = await auth_service.update_profile(db, current_user.id, data)
    if not user:
        return APIResponse(data=None, message="User not found", success=False)
    return APIResponse(data=UserResponse.model_validate(user), message="Profile updated", success=True)


@router.post("/change-password", response_model=APIResponse)
async def change_password(data: ChangePasswordRequest, current_user: CurrentUser, db: DBSession):
    await auth_service.change_password(db, current_user.id, data)
    return APIResponse(message="Password changed", success=True)
