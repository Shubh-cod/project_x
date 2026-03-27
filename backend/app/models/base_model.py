"""Abstract base: id (UUID), created_at, updated_at."""
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column, declared_attr

from app.db.base import Base


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
