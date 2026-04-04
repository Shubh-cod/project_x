"""Deal / Opportunity model."""
import uuid
from datetime import date, datetime
from sqlalchemy import String, Text, Numeric, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.models.user import User
from app.models.contact import Contact
from app.models.lead import Lead


class Deal(BaseModel):
    __tablename__ = "deals"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    contact_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lead_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("leads.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    stage: Mapped[str] = mapped_column(String(50), nullable=False, default="prospect", index=True)
    value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    close_date: Mapped[date | None] = mapped_column(nullable=True)
    probability: Mapped[int | None] = mapped_column(nullable=True)  # 0-100
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
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    won_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lost_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    contact: Mapped[Contact] = relationship("Contact", back_populates="deals", foreign_keys=[contact_id], lazy="selectin")
    lead: Mapped[Lead | None] = relationship("Lead", back_populates="deals", foreign_keys=[lead_id], lazy="selectin")
    assigned_to_user: Mapped[User | None] = relationship(
        "User",
        back_populates="deals",
        foreign_keys=[assigned_to],
        lazy="selectin",
    )
