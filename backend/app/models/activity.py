"""Activity model - feed for entity and global."""
import uuid
from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import BaseModel
from app.models.user import User


class Activity(BaseModel):
    __tablename__ = "activities"

    entity_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # contact, lead, deal
    entity_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON().with_variant(JSONB, "postgresql"), nullable=True)

    @property
    def extra_metadata(self) -> dict | None:
        return self.metadata_
