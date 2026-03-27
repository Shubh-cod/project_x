"""Note schemas."""
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NoteBase(BaseModel):
    content: str
    entity_type: str  # contact, lead, deal
    entity_id: UUID


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    content: str | None = None


class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    content: str
    entity_type: str
    entity_id: UUID
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime
