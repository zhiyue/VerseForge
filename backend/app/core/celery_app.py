from celery import Celery
from .config import settings

celery_app = Celery(
    "verseforge",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# 配置Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1小时超时
    worker_max_tasks_per_child=1000,  # 处理1000个任务后重启worker
    broker_connection_retry_on_startup=True,
)

# 自动发现并注册任务
celery_app.autodiscover_tasks([
    "app.agents.plot",
    "app.agents.character",
    "app.agents.scene",
    "app.agents.writing",
    "app.agents.qa",
    "app.agents.coherence",
], force=True)