# backend/src/models_app.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from src.database import Base

class App(Base):
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    template = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False, default="ready")

    # where the frontend should open for preview / download (served by backend)
    preview_url = Column(String(500), nullable=True)
    zip_url = Column(String(500), nullable=True)

    # anything extra (e.g., generation inputs, size, etc.)
    meta = Column(JSON, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
