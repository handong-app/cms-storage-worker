from celery import Celery
from src.core.config import EnvVariables

# Celery 인스턴스 생성
celery_app = Celery(
    "worker",
    broker=EnvVariables.RABBITMQ_URL,
    backend=EnvVariables.CELERY_RESULT_BACKEND,
)

from src.tasks import video_tasks

celery_app.autodiscover_tasks(["src.tasks"])