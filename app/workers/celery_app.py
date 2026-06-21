from app.core.config import settings

try:
    from celery import Celery
except ModuleNotFoundError:  # pragma: no cover - used only before dependencies are installed
    Celery = None


if Celery is not None:
    celery_app = Celery(
        "chat_data_platform",
        broker=settings.redis_url,
        backend=settings.redis_url,
    )
    celery_app.conf.update(task_track_started=True)
else:
    celery_app = None
