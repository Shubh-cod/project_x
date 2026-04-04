"""Note model - polymorphic attachment to contact, lead, or deal."""
import uuid
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.models.user import User


class Note(BaseModel):
    __tablename__ = "notes"

    content: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # contact, lead, deal
    entity_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_by_user: Mapped[User | None] = relationship(
        "User",
        foreign_keys=[created_by],
        lazy="selectin",
    )
