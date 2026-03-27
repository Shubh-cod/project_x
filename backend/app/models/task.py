"""Task model - polymorphic link to contact/lead/deal."""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.models.user import User
from app.utils.enums import TaskStatus, TaskPriority


class Task(BaseModel):
    __tablename__ = "tasks"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default=TaskPriority.MEDIUM.value, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=TaskStatus.TODO.value, index=True)
    # Polymorphic link: linked_to_type in (contact, lead, deal), linked_to_id = UUID
    linked_to_type: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    linked_to_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True, index=True)
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    assigned_to_user: Mapped[User | None] = relationship(
        "User",
        back_populates="tasks",
        foreign_keys=[assigned_to],
        lazy="selectin",
    )
