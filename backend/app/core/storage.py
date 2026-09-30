import json
import logging

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        use_ssl=settings.s3_use_ssl,
        config=Config(signature_version="s3v4"),
    )


def ensure_bucket() -> None:
    """Crea el bucket si no existe y aplica una política de lectura pública anónima
    (el backend guarda solo la key del objeto; la URL pública se resuelve con S3_PUBLIC_URL)."""
    client = get_s3_client()
    try:
        client.head_bucket(Bucket=settings.s3_bucket)
    except ClientError:
        try:
            client.create_bucket(Bucket=settings.s3_bucket)
        except ClientError as exc:
            logger.warning("Could not create bucket %s: %s", settings.s3_bucket, exc)
            return

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{settings.s3_bucket}/*",
            }
        ],
    }
    try:
        client.put_bucket_policy(Bucket=settings.s3_bucket, Policy=json.dumps(policy))
    except ClientError as exc:
        logger.warning("Could not apply the public policy to bucket %s: %s", settings.s3_bucket, exc)


def upload_bytes(*, key: str, data: bytes, content_type: str) -> None:
    client = get_s3_client()
    client.put_object(Bucket=settings.s3_bucket, Key=key, Body=data, ContentType=content_type)


def delete_object(key: str) -> None:
    client = get_s3_client()
    try:
        client.delete_object(Bucket=settings.s3_bucket, Key=key)
    except ClientError as exc:
        logger.warning("Could not delete object %s: %s", key, exc)


def build_public_url(key: str | None) -> str | None:
    if not key:
        return None
    return f"{settings.s3_public_url.rstrip('/')}/{settings.s3_bucket}/{key}"
