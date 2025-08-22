# backend/src/server/routes/apps.py
from datetime import datetime
import os
import shutil
from typing import List, Optional, Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import SessionLocal, Base, engine
from src.models_app import App as AppModel

router = APIRouter()

# --- ensure table exists on import (safe if already created) ---------------
Base.metadata.create_all(bind=engine, tables=[AppModel.__table__])

# --- DB session dependency --------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Schemas ---------------------------------------------------------------
class AppCreate(BaseModel):
    name: str
    template: Optional[str] = None
    preview_url: Optional[str] = None
    zip_url: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    status: Optional[str] = "ready"

class AppOut(BaseModel):
    id: int
    name: str
    template: Optional[str]
    status: str
    preview_url: Optional[str]
    zip_url: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

# --- Endpoints -------------------------------------------------------------

@router.post("/apps", response_model=AppOut)
def create_app(body: AppCreate, db: Session = Depends(get_db)):
    app = AppModel(
        name=body.name,
        template=body.template,
        preview_url=body.preview_url,
        zip_url=body.zip_url,
        meta=body.meta,
        status=body.status or "ready",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app

@router.get("/apps", response_model=List[AppOut])
def list_apps(db: Session = Depends(get_db)):
    rows = db.query(AppModel).order_by(AppModel.id.desc()).all()
    return rows

@router.get("/apps/{app_id}/meta", response_model=AppOut)
def get_app_meta(app_id: int, db: Session = Depends(get_db)):
    app = db.get(AppModel, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    return app

@router.delete("/apps/{app_id}")
def delete_app(
    app_id: int,
    purge_files: bool = Query(True, description="Also delete preview/zip on disk (if paths resolvable)"),
    db: Session = Depends(get_db),
):
    app = db.get(AppModel, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="App not found")

    # Best-effort file cleanup (safe no-op if not found)
    if purge_files:
        for path in (app.zip_url, app.preview_url):
            # Only try to remove if the backend stored actual filesystem paths.
            # If these are URLs, you can switch to app.meta["zip_path"], app.meta["preview_dir"] etc.
            if not path:
                continue
            # If your generator stored real disk paths in meta, prefer those:
            disk_file = None
            if app.meta:
                disk_file = app.meta.get("zip_path") if "zip" in (path or "") else app.meta.get("preview_path")
            candidate = disk_file or path
            try:
                if os.path.isdir(candidate):
                    shutil.rmtree(candidate, ignore_errors=True)
                elif os.path.isfile(candidate):
                    os.remove(candidate)
            except Exception:
                # swallow cleanup errors; DB will still be consistent
                pass

    db.delete(app)
    db.commit()
    return {"ok": True}
