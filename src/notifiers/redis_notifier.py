import json
import redis

from src.core.config import EnvVariables

redis_client = redis.StrictRedis(
    host=EnvVariables.REDIS_HOST,
    port=EnvVariables.REDIS_PORT,
    decode_responses=True
)

def publish_progress(video_id: str, status: str, progress: int = 0):
    message = {
        "videoId": video_id,
        "status": status,
        "progress": progress
    }
    redis_client.publish(EnvVariables.REDIS_CHANNEL, json.dumps(message))