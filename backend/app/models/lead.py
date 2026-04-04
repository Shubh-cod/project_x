"""Lead model."""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, Numeric, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.models.user import User
from app.models.contact import Contact
from app.models.tag import lead_tags
from app.utils.enums import LeadStatus, LeadPriority, LeadSource


class Lead(BaseModel):
    __tablename__ = "leads"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    contact_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source: Mapped[str] = mapped_column(String(50), nullable=False, default=LeadSource.OTHER.value)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=LeadStatus.NEW.value, index=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default=LeadPriority.MEDIUM.value, index=True)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    estimated_value: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Pipeline timestamps: when status changed to each stage (stored as JSON or separate columns)
    status_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    contact: Mapped[Contact] = relationship("Contact", back_populates="leads", foreign_keys=[contact_id], lazy="selectin")
    assigned_to_user: Mapped[User | None] = relationship(
        "User",
        back_populates="leads",
        foreign_keys=[assigned_to],
        lazy="selectin",
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary=lead_tags,
        back_populates="leads",
        lazy="selectin",
    )
    deals: Mapped[list["Deal"]] = relationship(
        "Deal",
        back_populates="lead",
        foreign_keys="Deal.lead_id",
        lazy="selectin",
    )
