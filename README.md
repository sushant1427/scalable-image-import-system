# Scalable Image Import System

A cloud-ready, multi-service backend application that imports images from a **public Google Drive folder**, stores them in **object storage (AWS S3 / MinIO)**, persists metadata in a **SQL database**, and exposes APIs to manage and view imported images. A simple frontend is included to trigger imports and display results.

---

## 🚀 Live Application

**Deployment Platform:** AWS EC2 (Dockerized Multi-Service Deployment)

**Working Site URL:** [http://13.201.224.10:8080/](http://13.201.224.10:8080/)

**GitHub Repository:** [https://github.com/sushant1427/scalable-image-import-system](https://github.com/sushant1427/scalable-image-import-system)

---

## 🧩 Problem Statement

Build a scalable backend system that:

* Accepts a public Google Drive folder URL
* Fetches all images from the folder
* Uploads them to cloud object storage
* Stores image metadata in a SQL database
* Exposes APIs to import and list images
* Provides a basic frontend for interaction

The system must be modular, scalable, fault-tolerant, and Dockerized.

---

## 🏗️ Architecture Overview

The application follows a **multi-service architecture**:

```
Frontend (HTML/CSS/JS)
        |
        v
API Service (FastAPI)
        |
        v
Redis Queue  ---> Worker Service
                       |
                       v
                Google Drive API
                       |
                       v
               Object Storage (MinIO / S3)
                       |
                       v
                MySQL Database
```

### Services Breakdown

| Service  | Responsibility                                       |
| -------- | ---------------------------------------------------- |
| Frontend | UI to submit Drive URL & view images                 |
| API      | Accepts requests, validates input, enqueues jobs     |
| Worker   | Downloads images, uploads to storage, saves metadata |
| Redis    | Job queue for async processing                       |
| MySQL    | Stores image metadata                                |
| MinIO    | S3-compatible object storage                         |

---

## ⚙️ Tech Stack

* **Backend:** Python, FastAPI
* **Worker:** Python, Redis Queue
* **Database:** MySQL
* **Object Storage:** MinIO (S3-compatible)
* **Queue:** Redis
* **Frontend:** HTML, CSS, JavaScript
* **Containerization:** Docker & Docker Compose
* **Deployment:** AWS EC2

---

## 📡 API Documentation

### 1️⃣ Import Images from Google Drive

**Endpoint:**

```
POST /import/google-drive
```

**Request Body (JSON):**

```json
{
  "folder_url": "https://drive.google.com/drive/folders/<FOLDER_ID>"
}
```

**Response:**

```json
{
  "message": "Import started successfully"
}
```

---

### 2️⃣ Get Imported Images

**Endpoint:**

```
GET /images
```

**Response:**

```json
[
  {
    "id": 1,
    "name": "image1.jpg",
    "google_drive_id": "abc123",
    "size": 204800,
    "mime_type": "image/jpeg",
    "storage_path": "http://<minio-url>/images/image1.jpg"
  }
]
```

---

## 🖥️ Frontend Features

* Input field for public Google Drive folder URL
* Button to trigger image import
* Table view of imported images
* Displays name, mime type, size, and storage link

---

## 🐳 Docker & Setup Instructions (AWS EC2 Deployment)

### Prerequisites

* Docker
* Docker Compose

### Clone Repository

```
git clone https://github.com/sushant1427/scalable-image-import-system.git
cd scalable-image-import-system
```

### Environment Variables

Create a `.env` file in the root directory:

```
DATABASE_URL=mysql+pymysql://admin:admin@db:3306/images
REDIS_HOST=redis
REDIS_PORT=6379
GOOGLE_API_KEY=your_google_api_key
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=images
S3_PUBLIC_BASE_URL=http://<EC2-IP>:9000/images
```

### Run Application

```
docker-compose up -d --build
```

Access:

* Frontend: `http://<EC2-IP>`
* API: `http://<EC2-IP>:8000`

---

## 📈 Scalability & Design Considerations (Cloud & EC2 Ready)

* **Asynchronous processing** using Redis + Worker
* **Loose coupling** between API and worker services
* **Retry-safe architecture** (jobs can be reprocessed)
* **Horizontal scaling** by adding more worker containers
* **S3-compatible storage** allows easy migration to AWS S3
* **Environment-based configuration** for portability

---

## 🔐 Security & Best Practices

* Secrets managed via environment variables
* Public Google Drive access only (read-only)
* Dockerized services for isolation
* Modular and clean code structure

---

## ✨ Optional Enhancements (Future Scope)

* Dropbox folder import
* Authentication & authorization
* Pagination & filters for `/images` API
* Monitoring & logging (Prometheus, Grafana)
* Kubernetes deployment

---

## 👨‍💻 Author

**Sushant Chavan**
Backend Developer
GitHub: [https://github.com/sushant1427](https://github.com/sushant1427)

---

✅ This project was built to demonstrate scalable backend architecture, cloud readiness, and production-grade engineering practices.
