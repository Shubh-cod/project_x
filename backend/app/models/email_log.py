"""Email activity log - outbound emails to contacts."""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.models.contact import Contact
from app.models.user import User


class EmailLog(BaseModel):
    __tablename__ = "email_logs"

    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body_preview: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    contact_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    sent_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    contact: Mapped[Contact] = relationship("Contact", foreign_keys=[contact_id], lazy="selectin")
    sent_by_user: Mapped[User | None] = relationship(
        "User",
        foreign_keys=[sent_by],
        lazy="selectin",
    )
