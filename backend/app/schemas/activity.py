"""Activity schemas."""
from uuid import UUID
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class ActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    entity_type: str
    entity_id: UUID
    action: str
    user_id: UUID | None
    metadata: dict | None
    created_at: datetime


class ActivityFeedFilters(BaseModel):
    user_id: UUID | None = None
    entity_type: str | None = None
    entity_id: UUID | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    page: int = 1
    page_size: int = 20
