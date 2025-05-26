import boto3
from app.core.config import EnvVariables

s3 = boto3.client(
    's3',
    aws_access_key_id=EnvVariables.ACCESS_KEY_ID,
    aws_secret_access_key=EnvVariables.SECRET_ACCESS_KEY,
    endpoint_url=EnvVariables.ENDPOINT,
    config=boto3.session.Config(signature_version=EnvVariables.SIGNATURE_VERSION),
    region_name='us-east-1',
)

BUCKET_NAME = 'cms'
