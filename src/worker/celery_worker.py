from celery import Celery
from src.core.config import EnvVariables


broker_url = EnvVariables.EXTERN_RABBITMQ_URL
result_backend = EnvVariables.CELERY_RESULT_BACKEND

celery_app = Celery("worker", broker=broker_url, backend=result_backend)

celery_app.conf.task_routes = {
    'transcode_video_task': {'queue': EnvVariables.CELERY_TRANSCODE_QUEUE}
}


from src.tasks import transcode_video_task

celery_app.autodiscover_tasks(["src.tasks"])