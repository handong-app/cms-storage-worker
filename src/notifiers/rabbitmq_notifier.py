import pika
import json
import threading
from src.core.config import EnvVariables
from pika.exceptions import StreamLostError

_connection = None
_channel = None
_lock = threading.Lock()

def _get_channel():
    global _connection, _channel
    with _lock:
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
    global _connection, _channel
    payload = {
        "videoId": video_id,
        "status": status,
        "progress": progress
    }

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            channel = _get_channel()
            channel.basic_publish(
                exchange='',
                routing_key=EnvVariables.TRANSCODE_STATUS_QUEUE,
                body=json.dumps(payload),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            print(f"✈️ Sent on attempt {attempt}: {payload}")
            break

        except StreamLostError as e:
            print(f"⚠️ Attempt {attempt}: StreamLostError (EOF). Reconnecting...")
            with _lock:
                _connection = None
                _channel = None
            if attempt == max_retries:
                print("❌ Max retries reached. Could not send message.")
                raise e

        except Exception as e:
            print(f"❌ Attempt {attempt}: Unexpected error: {e}")
            raise e