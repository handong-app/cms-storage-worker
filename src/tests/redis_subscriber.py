import os
import sys
import redis
import json

from src.core.config import EnvVariables

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

redis_client = redis.Redis(
    host=EnvVariables.TEST_REDIS_HOST,
    port=EnvVariables.TEST_REDIS_PORT,
    decode_responses=True
)

def main():
    pubsub = redis_client.pubsub()
    pubsub.subscribe(EnvVariables.TEST_REDIS_CHANNEL)

    print(f"✅ Subscribed to Redis channel: {EnvVariables.TEST_REDIS_CHANNEL}")
    print("📡 Waiting for messages...\n")

    for message in pubsub.listen():
        if message["type"] == "message":
            try:
                data = json.loads(message["data"])
                print(f"📬 Progress Update → Video ID: {data['videoId']}, "
                      f"Status: {data['status']}, Progress: {data['progress']}%")
            except json.JSONDecodeError:
                print(f"⚠️ Received non-JSON message: {message['data']}")

if __name__ == "__main__":
    main()