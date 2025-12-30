# Scalable Image Import System (Google Drive -> S3/MinIO)

This repo implements the **Backend Assignment: Scalable Image Import System from Google Drive** as a **multi-service** architecture with:
- **api-service** (FastAPI): accepts import requests, lists images in a public Google Drive folder, enqueues jobs.
- **worker-service**: consumes jobs, downloads files from Google Drive, uploads to S3/MinIO, persists metadata to SQL.
- **mysql**: SQL metadata store.
- **redis**: job queue.
- **frontend**: basic UI (static HTML + JS) to trigger imports and list images.

## Architecture (high-level)
1. `POST /import/google-drive` receives a public folder URL
2. API extracts folder id, lists images via Google Drive API (requires `GOOGLE_API_KEY`)
3. API enqueues one Redis job per image (`import_queue`)
4. Worker consumes jobs, downloads file bytes, uploads to S3/MinIO, stores metadata in MySQL
5. `GET /images` returns all imported images

## Requirements
- Docker + Docker Compose
- A Google Drive API key (for listing & downloading public files)
- S3-compatible object storage (AWS S3 or MinIO)

## Configuration (.env)
Create a `.env` file in repo root (or set env vars in your deploy):

```env
# Google Drive
GOOGLE_API_KEY=your_google_api_key

# Database
DATABASE_URL=mysql+pymysql://admin:admin@db:3306/images

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# S3 / MinIO
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=images
S3_REGION=us-east-1
S3_PUBLIC_BASE_URL=http://localhost:9000/images
```

Notes:
- For AWS S3: omit `S3_ENDPOINT_URL` and set `S3_PUBLIC_BASE_URL` to your CloudFront/S3 public URL pattern (or keep empty and rely on S3 object URL conventions).
- For MinIO (local), this repo includes a `minio` service and auto-creates the bucket.

## Run locally
```bash
docker compose up --build
```

Open:
- Frontend: http://localhost:8080
- API docs: http://localhost:8000/docs
- API health: http://localhost:8000/health

## API
### POST /import/google-drive
Request:
```json
{ "folder_url": "https://drive.google.com/drive/folders/<FOLDER_ID>" }
```

Response:
```json
{ "import_id": "...", "enqueued": 123 }
```

### GET /images
Optional filters:
- `?source=google-drive`
- `?import_id=<id>`

Response: list of image metadata rows.

## Scalability notes
- API only lists files and enqueues jobs (fast).
- Worker can be horizontally scaled: `docker compose up --scale worker=5`
- Redis queue decouples ingest from processing.
- Worker includes retry/backoff for transient failures.

## Deliverables
- Public GitHub repo URL
- Publicly accessible deployment URL
