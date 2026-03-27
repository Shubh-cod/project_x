"""Periodic cleanup: soft-delete purge, token cleanup."""
import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger("novacrm")


async def cleanup_tokens_and_soft_deletes(ctx: dict):
    """ARQ job: optional periodic cleanup of expired refresh tokens and old soft-deleted records."""
    # Redis TTL handles refresh token expiry; no explicit cleanup needed unless we want to scan keys.
    # Soft-delete purge: could delete contacts/leads that have been is_deleted=True for > N days.
    logger.info("Cleanup job ran at %s", datetime.now(timezone.utc).isoformat())
    return {"ok": True}
