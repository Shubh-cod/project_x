"""Shared FastAPI dependencies (get_db, get_current_user, etc.)."""
from typing import Annotated
from uuid import UUID

from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.user import User
from app.redis.client import get_redis
from app.redis.keys import refresh_token_key
from app.utils.security import decode_token
from app.utils.exceptions import UnauthorizedError, ForbiddenError
from app.config import get_settings

security = HTTPBearer(auto_error=False)


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> User:
    if not credentials:
        raise UnauthorizedError("Not authenticated")
    token = credentials.credentials
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise UnauthorizedError("Invalid or expired token")
    sub = payload.get("sub")
    if not sub:
        raise UnauthorizedError("Invalid token")
    try:
        user_id = UUID(sub)
    except ValueError:
        raise UnauthorizedError("Invalid token")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise UnauthorizedError("User not found")
    if not user.is_active:
        raise UnauthorizedError("User is disabled")
    return user


async def get_current_user_optional(
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> User | None:
    if not credentials:
        return None
    try:
        return await get_current_user(db, credentials)
    except UnauthorizedError:
        return None


def require_role(*roles: str):
    """Dependency that checks user has one of the given roles."""
    async def _check(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role.value not in roles:
            raise ForbiddenError("Insufficient permissions")
        return user
    return _check


# Type aliases for cleaner route signatures
DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_role("admin"))]
ManagerUser = Annotated[User, Depends(require_role("admin", "manager"))]
