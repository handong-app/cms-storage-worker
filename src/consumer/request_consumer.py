import json
import time
import pika

from pika.exceptions import AMQPConnectionError
from src.core.config import EnvVariables
from src.tasks.transcode_video_task import transcode_video_task
from src.utils.logging_utils import setup_logger


logger = setup_logger(__name__)


def connect_with_retry(host, retries=5, delay=3):
    for attempt in range(1, retries + 1):
        try:
            return pika.BlockingConnection(pika.ConnectionParameters(host=host))
        except AMQPConnectionError as e:
            print(f"[Consumer] ♻️  Connection attempt {attempt}/{retries} failed. Retrying in {delay}s...")
            time.sleep(delay)
    raise RuntimeError(f"❌  Could not connect to RabbitMQ at {host} after {retries} attempts")


def callback(ch, method, properties, body):
    logger.info(f"[Consumer] 📨  Received message from queue '{EnvVariables.TRANSCODE_REQUEST_QUEUE}': {body}")

    try:
        message = json.loads(body)
        file_key = message["fileKey"]
        filetype = message["filetype"]

        if filetype:
            if file_key:
                if filetype == "video":
                    logger.info(f"[Consumer] 🎬  Dispatching Celery task for: {file_key}")
                    transcode_video_task.delay(file_key)
                elif filetype == "audio":
                    logger.info(f"[Consumer] 🔊  Dispatching Celery task for: {file_key}")
                    # TODO: Audio 트렌스코드 테스크 구현
            else:
                logger.warning("[Consumer] 🫥  No filename in message")
        else:
            logger.warning("[Consumer] 🤷‍♂️  No filetype in message")



    except Exception as e:
        logger.exception(f"[Consumer] ❌  Failed to process message: {e}")

def main():
    logger.info(f"🚀  Connecting to RabbitMQ at {EnvVariables.RABBITMQ_HOST}...")
    connection = connect_with_retry(EnvVariables.RABBITMQ_HOST)
    channel = connection.channel()
    channel.queue_declare(queue=EnvVariables.TRANSCODE_REQUEST_QUEUE, durable=True)

    logger.info(f"🎧  Subscribing to queue: {EnvVariables.TRANSCODE_REQUEST_QUEUE}")
    channel.basic_consume(queue=EnvVariables.TRANSCODE_REQUEST_QUEUE, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    main()