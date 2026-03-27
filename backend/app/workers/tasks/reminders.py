"""Send task reminder notifications - schedule N minutes before due_date using ARQ."""
from datetime import datetime, timezone
from uuid import UUID
import arq


async def send_task_reminder(ctx: dict, task_id: str):
    """ARQ job: send a reminder for a task. task_id is UUID string."""
    # In production: send email/push. Here we just log.
    import logging
    logging.getLogger("novacrm").info("Task reminder: task_id=%s", task_id)
    # Optional: enqueue a webhook for task completion / reminder
    return {"task_id": task_id, "sent_at": datetime.now(timezone.utc).isoformat()}
