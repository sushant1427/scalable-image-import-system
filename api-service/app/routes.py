import os
import uuid
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from redis import Redis

from common.database import engine
from common.models import Image
from app.services.google_drive import extract_folder_id, list_images_in_folder

router = APIRouter()

class ImportRequest(BaseModel):
    folder_url: HttpUrl

def get_redis() -> Redis:
    host = os.getenv("REDIS_HOST", "redis")
    port = int(os.getenv("REDIS_PORT", "6379"))
    return Redis(host=host, port=port, decode_responses=True)

@router.post("/import/google-drive")
def import_google_drive(requests: ImportRequest):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY is not set")

    folder_id = extract_folder_id(str(requests.folder_url))
    if not folder_id:
        raise HTTPException(status_code=400, detail="Could not extract folder id from URL")

    files = list_images_in_folder(folder_id=folder_id, api_key=api_key)
    if not files:
        return {"import_id": None, "enqueued": 0}

    import_id = uuid.uuid4().hex
    r = get_redis()

    # enqueue one job per image
    enqueued = 0
    for file in files:
        job = {
            "source": "google-drive",
            "import_id": import_id,
            "google_drive_id": file["id"],
            "name": file.get("name"),
            "size": int(file.get("size", 0)) if file.get("size") else None,
            "mime_type": file.get("mimeType"),
        }
        r.lpush("import_queue", __import__("json").dumps(job))
        enqueued += 1

    return {"import_id": import_id, "enqueued": enqueued}

@router.get("/images")
def list_images(
    source: str | None = Query(default=None),
    import_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    with Session(engine) as db:
        q = db.query(Image)
        if source:
            q = q.filter(Image.source == source)
        if import_id:
            q = q.filter(Image.import_id == import_id)
        rows = q.order_by(Image.id.desc()).offset(offset).limit(limit).all()

        return [
            {
                "id": r.id,
                "name": r.name,
                "google_drive_id": r.google_drive_id,
                "size": r.size,
                "mime_type": r.mime_type,
                "storage_path": r.storage_path,
                "source": r.source,
                "import_id": r.import_id,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]
