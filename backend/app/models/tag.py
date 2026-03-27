"""Tag model - global tags attachable to contacts and leads."""
from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.db.base import Base

# Association tables for many-to-many
contact_tags = Table(
    "contact_tags",
    Base.metadata,
    Column("contact_id", ForeignKey("contacts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)
lead_tags = Table(
    "lead_tags",
    Base.metadata,
    Column("lead_id", ForeignKey("leads.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(BaseModel):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    contacts: Mapped[list["Contact"]] = relationship(
        "Contact",
        secondary=contact_tags,
        back_populates="tags",
        lazy="selectin",
    )
    leads: Mapped[list["Lead"]] = relationship(
        "Lead",
        secondary=lead_tags,
        back_populates="tags",
        lazy="selectin",
    )
