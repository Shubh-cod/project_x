"""Lead schemas."""
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

from app.utils.enums import LeadStatus, LeadPriority, LeadSource


class LeadBase(BaseModel):
    title: str
    contact_id: UUID
    source: str = LeadSource.OTHER.value
    status: str = LeadStatus.NEW.value
    priority: str = LeadPriority.MEDIUM.value
    assigned_to: UUID | None = None
    estimated_value: Decimal | None = None
    notes: str | None = None
    tags: List[str] | None = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    title: str | None = None
    contact_id: UUID | None = None
    source: str | None = None
    status: str | None = None
    priority: str | None = None
    assigned_to: UUID | None = None
    estimated_value: Decimal | None = None
    notes: str | None = None
    tags: List[str] | None = None


class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    contact_id: UUID
    source: str
    status: str
    priority: str
    assigned_to: UUID | None
    estimated_value: Decimal | None
    notes: str | None
    status_changed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []


class LeadConvertRequest(BaseModel):
    """Convert lead to contact (or create deal)."""
    create_deal: bool = False
    deal_title: str | None = None
    deal_value: float | None = None
