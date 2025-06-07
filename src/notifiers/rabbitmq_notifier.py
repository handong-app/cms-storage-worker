import pika
import json
from src.core.config import EnvVariables


_connection = None
_channel = None


def _get_channel():
    global _connection, _channel
    if _connection is None or _channel is None or _connection.is_closed or _channel.is_closed:
        credentials = pika.PlainCredentials(
            EnvVariables.EXTERN_RABBITMQ_USER,
            EnvVariables.EXTERN_RABBITMQ_PASSWORD
        )
        parameters = pika.ConnectionParameters(
            host=EnvVariables.EXTERN_RABBITMQ_HOST,
            port=EnvVariables.EXTERN_RABBITMQ_PORT,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        _connection = pika.BlockingConnection(parameters)
        _channel = _connection.channel()
        _channel.queue_declare(queue=EnvVariables.TRANSCODE_STATUS_QUEUE, durable=True)
    return _channel


def send_status(video_id: str, status: str, progress: int = 0):
    channel = _get_channel()

    payload = {
        "videoId": video_id,
        "status": status,
        "progress": progress
    }

    channel.basic_publish(
        exchange='',
        routing_key=EnvVariables.TRANSCODE_STATUS_QUEUE,
        body=json.dumps(payload),
        properties=pika.BasicProperties(
            delivery_mode=2  # 메시지를 영구적으로 만듦
        )
    )

    print(payload)
