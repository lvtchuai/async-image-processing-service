import boto3
from botocore.client import Config
import config

_s3 = boto3.client(
    "s3",
    endpoint_url=config.S3_ENDPOINT,
    aws_access_key_id=config.S3_ACCESS_KEY,
    aws_secret_access_key=config.S3_SECRET_KEY,
    region_name=config.S3_REGION,
    config=Config(signature_version="s3v4"),
)

def download_bytes(key: str) -> bytes:
    return _s3.get_object(Bucket=config.S3_BUCKET, Key=key)["Body"].read()

def upload_bytes(key: str, data: bytes, content_type: str):
    _s3.put_object(Bucket=config.S3_BUCKET, Key=key, Body=data, ContentType=content_type)
