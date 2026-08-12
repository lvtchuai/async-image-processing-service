import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import config

# Local (MinIO): có S3_ENDPOINT + key. Cloud (S3 thật): S3_ENDPOINT trống -> dùng endpoint AWS mặc định.
_kwargs = {"region_name": config.S3_REGION, "config": Config(signature_version="s3v4")}
if config.S3_ENDPOINT:
    _kwargs["endpoint_url"] = config.S3_ENDPOINT
if config.S3_ACCESS_KEY:
    _kwargs["aws_access_key_id"] = config.S3_ACCESS_KEY
    _kwargs["aws_secret_access_key"] = config.S3_SECRET_KEY
_s3 = boto3.client("s3", **_kwargs)

def ensure_bucket():
    """Tạo bucket nếu chưa có (idempotent) — hệ thống tự bootstrap, không cần tạo tay."""
    try:
        _s3.head_bucket(Bucket=config.S3_BUCKET)
    except ClientError:
        _s3.create_bucket(Bucket=config.S3_BUCKET)

def upload_bytes(key: str, data: bytes, content_type: str):
    _s3.put_object(Bucket=config.S3_BUCKET, Key=key, Body=data, ContentType=content_type)

def presigned_url(key: str, expires: int = 3600) -> str:
    # URL có chữ ký, hết hạn sau `expires` giây — không lộ credential storage.
    return _s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": config.S3_BUCKET, "Key": key},
        ExpiresIn=expires,
    )