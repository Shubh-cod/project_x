"""Automation rule schemas."""
from uuid import UUID
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class AutomationRuleCreate(BaseModel):
    name: str
    trigger_event: str  # lead_created, deal_stale, task_overdue
    conditions: dict[str, Any] | None = None
    action_type: str = "create_task"
    action_config: dict[str, Any] | None = None
    is_active: bool = True


class AutomationRuleUpdate(BaseModel):
    name: str | None = None
    trigger_event: str | None = None
    conditions: dict[str, Any] | None = None
    action_type: str | None = None
    action_config: dict[str, Any] | None = None
    is_active: bool | None = None


class AutomationRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    trigger_event: str
    conditions: dict[str, Any] | None
    action_type: str
    action_config: dict[str, Any] | None
    is_active: bool
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime
