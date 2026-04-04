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
        owner_id=user_id,
    )
    session.add(log_entry)
    await session.flush()
    await session.refresh(log_entry)
    return log_entry


async def get_by_id(session: AsyncSession, log_id: UUID, user_id: Optional[UUID] = None) -> EmailLog | None:
    q = select(EmailLog).where(EmailLog.id == log_id)
    if user_id is not None:
        q = q.where(EmailLog.owner_id == user_id)
    result = await session.execute(q)
    return result.scalar_one_or_none()


async def list_by_contact(
    session: AsyncSession,
    contact_id: UUID,
    user_id: Optional[UUID] = None,
    limit: int = 50,
) -> list[EmailLog]:
    q = (
        select(EmailLog)
        .where(EmailLog.contact_id == contact_id)
        .order_by(EmailLog.sent_at.desc())
        .limit(limit)
    )
    # ── Data isolation: only show logs owned by user ──
    if user_id is not None:
        q = q.where(EmailLog.owner_id == user_id)
    result = await session.execute(q)
    return list(result.scalars().all())
