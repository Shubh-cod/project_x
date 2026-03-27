"""Deal schemas."""
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class DealBase(BaseModel):
    title: str
    contact_id: UUID
    lead_id: UUID | None = None
    stage: str = "prospect"
    value: Decimal = 0
    currency: str = "USD"
    close_date: date | None = None
    probability: int | None = None
    assigned_to: UUID | None = None
    notes: str | None = None


class DealCreate(DealBase):
    pass


class DealUpdate(BaseModel):
    title: str | None = None
    contact_id: UUID | None = None
    lead_id: UUID | None = None
    stage: str | None = None
    value: Decimal | None = None
    currency: str | None = None
    close_date: date | None = None
    probability: int | None = None
    assigned_to: UUID | None = None
    notes: str | None = None
    won_reason: str | None = None
    lost_reason: str | None = None


class DealResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    contact_id: UUID
    lead_id: UUID | None
    stage: str
    value: Decimal
    currency: str
    close_date: date | None
    probability: int | None
    assigned_to: UUID | None
    notes: str | None
    won_reason: str | None
    lost_reason: str | None
    created_at: datetime
    updated_at: datetime


class DealPipelineStage(BaseModel):
    stage: str
    count: int
    total_value: float


class DealPipelineResponse(BaseModel):
    stages: list[DealPipelineStage]
