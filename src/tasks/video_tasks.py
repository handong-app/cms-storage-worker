from src.worker.celery_worker import celery_app
from src.services.transcode_service import transcode_video
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="transcode_video_task")
def transcode_video_task(filename: str):
    transcode_video(filename)
