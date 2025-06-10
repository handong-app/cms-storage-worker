import pika
import json
from src.core.config import EnvVariables
from src.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

def main():
    file_type = "video"
    # filename = "1748191347517-cap-ucc.mp4"
    filename = "wak.mp4"

    payload = {
        "file_type": file_type,
        "filename": filename
    }

    logger.info("[Producer] Connecting to RabbitMQ...")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=EnvVariables.EXTERN_RABBITMQ_HOST))
    channel = connection.channel()

    queue_name = EnvVariables.TEST_TRANSCODE_REQUEST_QUEUE
    channel.queue_declare(queue=queue_name, durable=True)

    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(payload),
        properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
    )

    logger.info(f"[Producer] Message published to '{queue_name}': {payload}")
    connection.close()

if __name__ == "__main__":
    main()