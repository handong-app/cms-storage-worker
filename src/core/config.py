import os
from dotenv import load_dotenv

load_dotenv()

class EnvVariables:
    # S3 config
    ACCESS_KEY_ID = os.getenv('ACCESS_KEY_ID')
    SECRET_ACCESS_KEY = os.getenv('SECRET_ACCESS_KEY')
    ENDPOINT = os.getenv('ENDPOINT')
    S3_FORCE_PATH_STYLE = os.getenv('S3_FORCE_PATH_STYLE')
    SIGNATURE_VERSION = os.getenv('SIGNATURE_VERSION')

    # Celery + RabbitMQ
    EXTERN_RABBITMQ_HOST = os.getenv('EXTERN_RABBITMQ_HOST')
    EXTERN_RABBITMQ_PORT = os.getenv('EXTERN_RABBITMQ_PORT')
    EXTERN_RABBITMQ_USER = os.getenv('EXTERN_RABBITMQ_USER')
    EXTERN_RABBITMQ_PASSWORD = os.getenv('EXTERN_RABBITMQ_PASSWORD')
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
    RABBITMQ_URL: str = os.getenv('RABBITMQ_URL', "amqp://guest:guest@rabbitmq:5672//")
    CELERY_RESULT_BACKEND: str = os.getenv('CELERY_RESULT_BACKEND', "rpc://")
    TRANSCODE_STATUS_QUEUE = os.getenv('TRANSCODE_STATUS_QUEUE', "transcode.status")
    TRANSCODE_REQUEST_QUEUE = os.getenv('TRANSCODE_REQUEST_QUEUE', "transcode.request")

    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_CHANNEL = os.getenv("REDIS_CHANNEL", "transcode.status")

    # For test
    # 테스트용 RabbitMQ 연결 설정
    TEST_RABBITMQ_HOST = os.getenv("TEST_RABBITMQ_HOST", "rabbitmq")
    TEST_RABBITMQ_URL = os.getenv("TEST_RABBITMQ_URL", "amqp://guest:guest@localhost:5672//")
    TEST_TRANSCODE_REQUEST_QUEUE = os.getenv("TEST_TRANSCODE_REQUEST_QUEUE", "transcode.request")
    TEST_TRANSCODE_STATUS_QUEUE = os.getenv("TEST_TRANSCODE_STATUS_QUEUE", "transcode.status")

    # 테스트용 Redis 설정
    TEST_REDIS_HOST = os.getenv("TEST_REDIS_HOST", "redis")
    TEST_REDIS_PORT = os.getenv("TEST_REDIS_PORT", 6379)
    TEST_REDIS_CHANNEL = os.getenv("TEST_REDIS_CHANNEL", "transcode.status")

    @staticmethod
    def get_routes_by_prefix(prefix):
        """주어진 prefix로 시작하는 .env 값을 배열로 반환."""
        routes = []
        for key, value in os.environ.items():
            if key.startswith(prefix):
                routes.append(value)
        return routes

    @staticmethod
    def get_routes_by_postfix(postfix):
        """주어진 postfix로 끝나는 .env 값을 배열로 반환."""
        routes = []
        for key, value in os.environ.items():
            if key.endswith(postfix):
                routes.append(value)
        return routes
