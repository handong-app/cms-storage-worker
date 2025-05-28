import pika
import json

from src.core.config import EnvVariables


def send_status(video_id: str, status: str, progress: int = 0):
    connection = pika.BlockingConnection(pika.ConnectionParameters(EnvVariables.RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=EnvVariables.TRANSCODE_STATUS_QUEUE)

    payload = {
        "videoId": video_id,
        "status": status,
        "progress": progress
    }

    channel.basic_publish(
        exchange='',
        routing_key=EnvVariables.TRANSCODE_STATUS_QUEUE,
        body=json.dumps(payload)
    )
    connection.close()