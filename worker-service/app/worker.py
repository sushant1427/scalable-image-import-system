import os
import json
import time
import traceback
import requests
from redis import Redis
from sqlalchemy.orm import sessionmaker

from common.database import engine, Base
from common.models import Image
from app.storage.s3 import get_s3_client, build_public_url

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(bind=engine)

def get_redis() -> Redis:
    host = os.getenv("REDIS_HOST", "redis")
    port = int(os.getenv("REDIS_PORT", "6379"))
    return Redis(host=host, port=port, decode_responses=True)

def download_drive_file(file_id: str, api_key: str) -> bytes:
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}"
    parameters = {"alt": "media", "key": api_key}
    response = requests.get(url, params=parameters, timeout=60)
    response.raise_for_status()
    return response.content

def upload_bytes_to_s3(data: bytes, key: str, content_type: str | None) -> str:
    s3 = get_s3_client()
    bucket = os.getenv("S3_BUCKET", "images")
    extra = {}
    if content_type:
        extra["ContentType"] = content_type
    s3.put_object(Bucket=bucket, Key=key, Body=data, **extra)
    return build_public_url(key)

def process_job(job: dict):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set")

    file_id = job["google_drive_id"]
    name = job.get("name") or f"{file_id}.img"
    mime_type = job.get("mime_type") or "application/octet-stream"
    size = job.get("size")

    # download
    content = download_drive_file(file_id, api_key)

    # upload (use import_id prefix for grouping)
    import_id = job.get("import_id") or "no-import-id"
    key = f"{import_id}/{file_id}-{name}"

    storage_path = upload_bytes_to_s3(content, key=key, content_type=mime_type)

    # persist
    db = SessionLocal()
    try:
        row = Image(
            name=name,
            google_drive_id=file_id,
            size=size if size is not None else len(content),
            mime_type=mime_type,
            storage_path=storage_path,
            source=job.get("source", "google-drive"),
            import_id=import_id,
        )
        db.add(row)
        db.commit()
    finally:
        db.close()

def main():
    r = get_redis()
    print("Worker started. Waiting for jobs on Redis list 'import_queue'...")

    while True:
        item = r.brpop("import_queue", timeout=5)
        if not item:
            continue

        _, payload = item
        try:
            job = json.loads(payload)
        except Exception:
            print("Invalid job payload:", payload)
            continue

        # basic retry with exponential backoff
        max_attempts = 5
        attempt = 0
        while True:
            attempt += 1
            try:
                process_job(job)
                print(f"Processed file_id={job.get('google_drive_id')} attempt={attempt}")
                break
            except Exception as e:
                print(f"Job failed attempt={attempt}/{max_attempts}: {e}")
                traceback.print_exc()
                if attempt >= max_attempts:
                    # push to dead-letter list for inspection
                    r.lpush("import_dead_letter", payload)
                    break
                time.sleep(min(2 ** attempt, 30))

if __name__ == "__main__":
    main()
