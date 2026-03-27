"""Shared: PaginatedResponse, MessageResponse, etc."""
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class MessageResponse(BaseModel):
    message: str
    success: bool = True


class PaginatedResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True)

    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int


class APIResponse(BaseModel, Generic[T]):
    """Standard envelope: { data, message, success }."""
    data: Optional[T] = None
    message: Optional[str] = None
    success: bool = True
