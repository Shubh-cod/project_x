"""Authentication: register, login, logout, refresh, profile, change password."""
from uuid import UUID
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.config import get_settings
from app.redis.client import get_redis
from app.redis.keys import refresh_token_key
from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.utils.enums import UserRole
from app.utils.exceptions import UnauthorizedError, ConflictError
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, ChangePasswordRequest
from app.schemas.user import UserProfileUpdate


settings = get_settings()


async def register(session: AsyncSession, data: RegisterRequest) -> User:
    result = await session.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise ConflictError("Email already registered")
    user = User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        role=UserRole.agent,
    )
    session.add(user)
    await session.flush()
    return user


async def login(session: AsyncSession, data: LoginRequest) -> tuple[User, TokenResponse]:
    result = await session.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password")
    if not user.is_active:
        raise UnauthorizedError("Account is disabled")
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    redis = await get_redis()
    key = refresh_token_key(user.id)
    await redis.setex(key, settings.refresh_token_expire_seconds, refresh_token)
    expires_in = settings.access_token_expire_minutes * 60
    return user, TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
    )


async def logout(user_id: UUID) -> None:
    redis = await get_redis()
    await redis.delete(refresh_token_key(user_id))


async def refresh_tokens(session: AsyncSession, refresh_token: str) -> TokenResponse:
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise UnauthorizedError("Invalid refresh token")
    sub = payload.get("sub")
    if not sub:
        raise UnauthorizedError("Invalid refresh token")
    user_id = UUID(sub)
    redis = await get_redis()
    key = refresh_token_key(user_id)
    stored = await redis.get(key)
    if stored != refresh_token:
        raise UnauthorizedError("Refresh token expired or invalid")
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or disabled")
    access_token = create_access_token(user.id)
    expires_in = settings.access_token_expire_minutes * 60
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
    )


async def get_profile(session: AsyncSession, user_id: UUID) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def update_profile(session: AsyncSession, user_id: UUID, data: UserProfileUpdate) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if data.full_name is not None:
        user.full_name = data.full_name
    await session.flush()
    return user


async def change_password(
    session: AsyncSession,
    user_id: UUID,
    data: ChangePasswordRequest,
) -> None:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise UnauthorizedError("User not found")
    if not verify_password(data.current_password, user.hashed_password):
        raise UnauthorizedError("Current password is incorrect")
    user.hashed_password = get_password_hash(data.new_password)
    await session.flush()
