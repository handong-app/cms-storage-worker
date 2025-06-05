import pika
import json
from src.core.config import EnvVariables


def send_status(video_id: str, status: str, progress: int = 0):
    host = EnvVariables.EXTERN_RABBITMQ_HOST
    port = EnvVariables.EXTERN_RABBITMQ_PORT
    user = EnvVariables.EXTERN_RABBITMQ_USER
    password = EnvVariables.EXTERN_RABBITMQ_PASSWORD
    queue_name = EnvVariables.TRANSCODE_STATUS_QUEUE

    credentials = pika.PlainCredentials(user, password)
    parameters = pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300
    )

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    payload = {
        "videoId": video_id,
        "status": status,
        "progress": progress
    }

    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(payload),
        properties=pika.BasicProperties(
            delivery_mode=2  # make message persistent
        )
    )
    connection.close()