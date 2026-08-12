import boto3
from botocore.client import Config
import config

# Local (MinIO): có S3_ENDPOINT + key. Cloud (S3 thật): S3_ENDPOINT trống -> endpoint AWS mặc định.
_kwargs = {"region_name": config.S3_REGION, "config": Config(signature_version="s3v4")}
if config.S3_ENDPOINT:
    _kwargs["endpoint_url"] = config.S3_ENDPOINT
if config.S3_ACCESS_KEY:
    _kwargs["aws_access_key_id"] = config.S3_ACCESS_KEY
    _kwargs["aws_secret_access_key"] = config.S3_SECRET_KEY
_s3 = boto3.client("s3", **_kwargs)

def download_bytes(key: str) -> bytes:
    return _s3.get_object(Bucket=config.S3_BUCKET, Key=key)["Body"].read()

def upload_bytes(key: str, data: bytes, content_type: str):
    _s3.put_object(Bucket=config.S3_BUCKET, Key=key, Body=data, ContentType=content_type)
