"""ARQ WorkerSettings and Redis pool config."""
import arq
from app.config import get_settings

settings = get_settings()


async def startup(ctx):
    pass


async def shutdown(ctx):
    pass


def get_worker_settings():
    from app.workers.tasks import reminders, cleanup
    return arq.WorkerSettings(
        redis_settings=arq.connections.RedisSettings.from_dsn(settings.arq_redis_url),
        on_startup=startup,
        on_shutdown=shutdown,
        functions=[reminders.send_task_reminder, cleanup.cleanup_tokens_and_soft_deletes],
    )
