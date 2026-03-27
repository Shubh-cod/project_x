"""Contact model."""
import uuid
from sqlalchemy import String, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

from app.models.base_model import BaseModel
from app.models.user import User
from app.models.tag import Tag, contact_tags


class Contact(BaseModel):
    __tablename__ = "contacts"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)  # web, referral, etc.
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    assigned_to_user: Mapped[User | None] = relationship(
        "User",
        back_populates="contacts",
        foreign_keys=[assigned_to],
        lazy="selectin",
    )
    tags: Mapped[list[Tag]] = relationship(
        "Tag",
        secondary=contact_tags,
        back_populates="contacts",
        lazy="selectin",
    )
    leads: Mapped[list["Lead"]] = relationship(
        "Lead",
        back_populates="contact",
        foreign_keys="Lead.contact_id",
        lazy="selectin",
    )
    deals: Mapped[list["Deal"]] = relationship(
        "Deal",
        back_populates="contact",
        foreign_keys="Deal.contact_id",
        lazy="selectin",
    )
