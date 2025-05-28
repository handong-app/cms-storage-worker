from src.utils.logging_utils import setup_logger
from src.worker.celery_worker import celery_app
from src.services.transcode_service import transcode_video


logger = setup_logger(__name__)

@celery_app.task(name="transcode_video_task")
def transcode_video_task(filename: str):
    logger.info(f"[Task] Task received for filename: {filename}")
    transcode_video(filename)
