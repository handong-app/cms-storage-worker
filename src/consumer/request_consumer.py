import json
import time
import pika

from pika.exceptions import AMQPConnectionError
from src.core.config import EnvVariables
from src.tasks.transcode_video_task import transcode_video_task
from src.utils.logging_utils import setup_logger


logger = setup_logger(__name__)


def connect_with_retry(host, port, user, password, retries=5, delay=3):
    credentials = pika.PlainCredentials(user, password)
    parameters = pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300
    )
    for attempt in range(1, retries + 1):
        try:
            return pika.BlockingConnection(parameters)
        except AMQPConnectionError:
            logger.warning(f"[Consumer] ♻️  Connection attempt {attempt}/{retries} failed. Retrying in {delay}s...")
            time.sleep(delay)
    raise RuntimeError(f"❌  Could not connect to RabbitMQ at {host}:{port} after {retries} attempts")

def callback(ch, method, properties, body):
    logger.info(f"[Consumer] 📨  Received message: {body}")

    try:
        message = json.loads(body)
        file_key = message["fileKey"]
        filetype = message["filetype"]

        if filetype and file_key:
            if filetype == "video":
                logger.info(f"[Consumer] 🎬  Dispatching Celery task for: {file_key}")
                transcode_video_task.delay(file_key)
            elif filetype == "audio":
                logger.info(f"[Consumer] 🔊  Dispatching Audio Transcode Task for: {file_key}")
                # TODO: Audio 트렌스코드 구현
        else:
            logger.warning("[Consumer] 🫥  Missing filename or filetype in message")

    except Exception as e:
        logger.exception(f"[Consumer] ❌  Failed to process message: {e}")



    except Exception as e:
        logger.exception(f"[Consumer] ❌  Failed to process message: {e}")

def main():
    host = EnvVariables.EXTERN_RABBITMQ_HOST
    port = EnvVariables.EXTERN_RABBITMQ_PORT
    user = EnvVariables.EXTERN_RABBITMQ_USER
    password = EnvVariables.EXTERN_RABBITMQ_PASSWORD
    queue_name = EnvVariables.TRANSCODE_REQUEST_QUEUE

    logger.info(f"🚀  Connecting to RabbitMQ at {host}:{port}...")
    connection = connect_with_retry(host, port, user, password)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    logger.info(f"🎧  Subscribing to queue: {queue_name}")
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
if __name__ == "__main__":
    main()