"""Generic paginator utility for async SQLAlchemy."""
from typing import Generic, List, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


async def paginate(
    session: AsyncSession,
    query_select: select,
    page: int = 1,
    page_size: int = 20,
) -> tuple[List[T], int]:
    """
    Execute a paginated query. Expects query_select to be a select() statement.
    Returns (items, total_count).
    """
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20
    offset = (page - 1) * page_size

    # Count total (strip order_by for count subquery if needed)
    count_stmt = select(func.count()).select_from(query_select.subquery())
    total_result = await session.execute(count_stmt)
    total = total_result.scalar_one()

    # Fetch page
    stmt = query_select.offset(offset).limit(page_size)
    result = await session.execute(stmt)
    items = list(result.scalars().all())

    return items, total
