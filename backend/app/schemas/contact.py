"""Contact schemas."""
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ContactBase(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    company: str | None = None
    address: str | None = None
    source: str | None = None
    notes: str | None = None
    assigned_to: UUID | None = None
    tags: List[str] | None = None  # tag names for create/update


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    company: str | None = None
    address: str | None = None
    source: str | None = None
    notes: str | None = None
    assigned_to: UUID | None = None
    tags: List[str] | None = None


class ContactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str | None
    phone: str | None
    company: str | None
    address: str | None
    source: str | None
    notes: str | None
    assigned_to: UUID | None
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []


class ContactListFilters(BaseModel):
    name: str | None = None
    email: str | None = None
    tag: str | None = None
    assigned_to: UUID | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    page: int = 1
    page_size: int = 20
