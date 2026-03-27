"""Task schemas."""
from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.utils.enums import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None
    priority: str = TaskPriority.MEDIUM.value
    status: str = TaskStatus.TODO.value
    linked_to_type: str | None = None  # contact, lead, deal
    linked_to_id: UUID | None = None
    assigned_to: UUID | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    priority: str | None = None
    status: str | None = None
    linked_to_type: str | None = None
    linked_to_id: UUID | None = None
    assigned_to: UUID | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    due_date: datetime | None
    priority: str
    status: str
    linked_to_type: str | None
    linked_to_id: UUID | None
    assigned_to: UUID | None
    created_at: datetime
    updated_at: datetime
