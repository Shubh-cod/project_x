"""AutomationRule model - trigger-based task creation rules."""
import uuid
from sqlalchemy import String, Text, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.models.user import User


class AutomationRule(BaseModel):
    __tablename__ = "automation_rules"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    trigger_event: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # lead_created, deal_stale, task_overdue
    conditions: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )
    action_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="create_task"
    )  # create_task
    action_config: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )  # {title_template, priority, due_in_hours}
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    creator: Mapped[User | None] = relationship(
        "User", foreign_keys=[created_by], lazy="selectin"
    )
