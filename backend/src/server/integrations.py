# backend/src/server/integrations.py
import os
import shutil
from datetime import datetime
from typing import Optional, Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.models_app import App as AppModel

router = APIRouter()

# --- DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Request/response models
class AppGenBody(BaseModel):
    name: str = Field(default="My App")
    template: str = Field(default="react-lite")
    # accept either `prompt` or legacy UI field `spec`
    prompt: Optional[str] = None
    spec: Optional[str] = None

    # pydantic v1 compatibility: allow both field names to populate
    class Config:
        allow_population_by_field_name = True
        extra = "ignore"

class AppGenResult(BaseModel):
    app_id: int
    preview_url: Optional[str]
    zip_url: Optional[str]

# helpers
def _apps_dir() -> str:
    out = "/models/apps"
    os.makedirs(out, exist_ok=True)
    return out

def _write_preview(app_dir: str):
    idx = os.path.join(app_dir, "index.html")
    os.makedirs(app_dir, exist_ok=True)
    with open(idx, "w", encoding="utf-8") as f:
        f.write("""<!doctype html>
<html><head><meta charset="utf-8"><title>App Preview</title></head>
<body style="font-family:system-ui;padding:20px;background:#0b1220;color:#fff">
  <h1>App preview</h1>
  <p>If you see this, preview routing works.</p>
</body></html>""")

def _write_zip(app_dir: str, zip_path: str):
    base = os.path.dirname(zip_path)
    os.makedirs(base, exist_ok=True)
    shutil.make_archive(zip_path[:-4], "zip", app_dir)

@router.post("/appgen/generate", response_model=AppGenResult)
def appgen_generate(body: AppGenBody, db: Session = Depends(get_db)):
    # normalize prompt
    prompt = (body.prompt or body.spec or "").strip()
    if not prompt:
        raise HTTPException(status_code=422, detail="prompt is required")

    # create db record early to get id
    app_row = AppModel(
        name=body.name,
        template=body.template,
        status="building",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(app_row)
    db.commit()
    db.refresh(app_row)

    # derive paths
    apps_root = _apps_dir()
    app_dir = os.path.join(apps_root, str(app_row.id))
    preview_dir = app_dir  # serve index.html from here
    zip_out = os.path.join(apps_root, f"{app_row.id}.zip")

    # fake “generation”: produce preview + zip
    try:
        _write_preview(preview_dir)
        _write_zip(preview_dir, zip_out)
    except Exception as e:
        app_row.status = "error"
        db.commit()
        raise HTTPException(status_code=500, detail=f"generation failed: {e}")

    # URLs that nginx exposes (/api/apps/<id> and /api/apps/<id>.zip)
    preview_url = f"/api/apps/{app_row.id}"
    zip_url = f"/api/apps/{app_row.id}.zip"

    # finalize row
    app_row.status = "ready"
    app_row.preview_url = preview_url
    app_row.zip_url = zip_url
    app_row.meta = {
        "prompt": prompt,
        "paths": {"preview_dir": preview_dir, "zip_path": zip_out},
    }
    app_row.updated_at = datetime.utcnow()
    db.commit()

    return AppGenResult(app_id=app_row.id, preview_url=preview_url, zip_url=zip_url)

# Static file serving (preview + zip)
from fastapi.responses import FileResponse, HTMLResponse

@router.get("/apps/{app_id}")
def serve_app_preview(app_id: int):
    idx = f"/models/apps/{app_id}/index.html"
    if not os.path.exists(idx):
        raise HTTPException(status_code=404, detail="preview not found")
    return HTMLResponse(open(idx, "r", encoding="utf-8").read())

@router.get("/apps/{app_id}.zip")
def serve_app_zip(app_id: int):
    zp = f"/models/apps/{app_id}.zip"
    if not os.path.exists(zp):
        raise HTTPException(status_code=404, detail="zip not found")
    return FileResponse(zp, media_type="application/zip", filename=f"app-{app_id}.zip")
