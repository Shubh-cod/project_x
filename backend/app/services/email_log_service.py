"""Email activity log - log outbound emails to contacts."""
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.email_log import EmailLog
from app.schemas.email_log import EmailLogCreate


async def create(
    session: AsyncSession,
    data: EmailLogCreate,
    user_id: Optional[UUID] = None,
) -> EmailLog:
    log_entry = EmailLog(
        subject=data.subject,
        body_preview=data.body_preview,
        sent_at=datetime.now(timezone.utc),
        contact_id=data.contact_id,
        sent_by=user_id,
    )
    session.add(log_entry)
    await session.flush()
    await session.refresh(log_entry)
    return log_entry


async def get_by_id(session: AsyncSession, log_id: UUID) -> EmailLog | None:
    result = await session.execute(select(EmailLog).where(EmailLog.id == log_id))
    return result.scalar_one_or_none()


async def list_by_contact(
    session: AsyncSession,
    contact_id: UUID,
    limit: int = 50,
) -> list[EmailLog]:
    result = await session.execute(
        select(EmailLog)
        .where(EmailLog.contact_id == contact_id)
        .order_by(EmailLog.sent_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
