"""Tag schemas."""
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: str | None = None


class TagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime


class TagAttachRequest(BaseModel):
    tag_ids: list[UUID]
