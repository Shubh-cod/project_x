"""Email log schemas."""
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class EmailLogCreate(BaseModel):
    subject: str
    body_preview: str | None = None
    contact_id: UUID


class EmailLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    subject: str
    body_preview: str | None
    sent_at: datetime
    contact_id: UUID
    sent_by: UUID | None
    created_at: datetime
    updated_at: datetime


class SearchResultItem(BaseModel):
    """Single item in global search (contact, lead, or deal)."""
    type: str  # contact, lead, deal
    id: UUID
    title: str  # name or title
    subtitle: str | None = None


class SearchResponse(BaseModel):
    contacts: list[SearchResultItem] = []
    leads: list[SearchResultItem] = []
    deals: list[SearchResultItem] = []
