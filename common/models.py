from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(512), nullable=False)
    google_drive_id = Column(String(128), nullable=False, index=True)
    size = Column(Integer, nullable=True)
    mime_type = Column(String(128), nullable=True)
    storage_path = Column(String(1024), nullable=False)
    source = Column(String(64), nullable=False, default="google-drive")
    import_id = Column(String(64), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
