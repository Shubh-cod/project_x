"""User model."""
import uuid
from sqlalchemy import String, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.utils.enums import UserRole


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.agent,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships (for assigned_* reverse refs from other models)
    contacts: Mapped[list["Contact"]] = relationship(
        "Contact",
        back_populates="assigned_to_user",
        foreign_keys="Contact.assigned_to",
        lazy="selectin",
    )
    leads: Mapped[list["Lead"]] = relationship(
        "Lead",
        back_populates="assigned_to_user",
        foreign_keys="Lead.assigned_to",
        lazy="selectin",
    )
    deals: Mapped[list["Deal"]] = relationship(
        "Deal",
        back_populates="assigned_to_user",
        foreign_keys="Deal.assigned_to",
        lazy="selectin",
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="assigned_to_user",
        foreign_keys="Task.assigned_to",
        lazy="selectin",
    )
