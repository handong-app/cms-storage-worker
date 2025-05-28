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
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672//"
    CELERY_RESULT_BACKEND: str = "rpc://"

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
