import os
import boto3

def get_s3_client():
    endpoint_url = os.getenv("S3_ENDPOINT_URL") or None
    access = os.getenv("S3_ACCESS_KEY")
    secret = os.getenv("S3_SECRET_KEY")
    region = os.getenv("S3_REGION", "us-east-1")

    session = boto3.session.Session()
    return session.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access,
        aws_secret_access_key=secret,
        region_name=region,
    )

def build_public_url(key: str) -> str:
    base = os.getenv("S3_PUBLIC_BASE_URL")
    bucket = os.getenv("S3_BUCKET", "images")
    if base:
        return f"{base.rstrip('/')}/{key}"
    # fallback: s3:// style
    return f"s3://{bucket}/{key}"
