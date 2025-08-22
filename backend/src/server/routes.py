from datetime import datetime
import os
import shutil
from typing import Any, Dict, List, Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.models import Run, RunEvent, RunStatus, Workflow, Model

router = APIRouter()

# --- DB session dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Health ---
@router.get("/health")
def health():
    return {"status": "ok"}

# ---------- Feature flags ----------
@router.get("/features")
def get_features():
    return {
        "mcp": os.getenv("ENABLE_MCP", "0") == "1",
        "n8n": os.getenv("ENABLE_N8N", "0") == "1",
        "appgen": os.getenv("ENABLE_APPGEN", "1") == "1",
    }

# ---------- Create run with pipeline spec ----------
class StepSpec(BaseModel):
    type: str
    params: Dict[str, Any] = Field(default_factory=dict)

class PipelineSpec(BaseModel):
    steps: List[StepSpec]

class CreateRunBody(BaseModel):
    pipeline: PipelineSpec
    name: Optional[str] = None

@router.post("/runs")
def create_run(body: CreateRunBody, db: Session = Depends(get_db)):
    wf = Workflow(
        name=body.name or "ad‑hoc",
        pipeline_spec=body.pipeline.dict()
    )
    db.add(wf)
    db.flush()

    run = Run(workflow_id=wf.id, status=RunStatus.queued, metrics=None, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    db.add(run)
    db.flush()

    db.add(RunEvent(
        run_id=run.id,
        ts=datetime.utcnow(),
        level="info",
        title="Run queued",
        detail="Awaiting agent pickup"
    ))
    db.commit()

    return {"run_id": run.id}

# --- Chat -> create run (legacy quick path) ---
class StartTrainRequest(BaseModel):
    prompt: str

@router.post("/chat/start-train")
def start_train(req: StartTrainRequest, db: Session = Depends(get_db)):
    run = Run(status=RunStatus.queued, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    db.add(run)
    db.commit()
    db.refresh(run)

    db.add(RunEvent(
        run_id=run.id,
        ts=datetime.utcnow(),
        level="info",
        title="Run queued",
        detail="Awaiting agent pickup",
    ))
    db.commit()

    return {"run_id": run.id}

# --- Runs ---
@router.get("/runs/{run_id}")
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return {
        "id": run.id,
        "status": run.status.value if hasattr(run.status, "value") else str(run.status),
        "metrics": run.metrics,
        "created_at": run.created_at,
        "updated_at": run.updated_at,
    }

@router.get("/runs")
def list_runs(db: Session = Depends(get_db)):
    rows = db.query(Run).order_by(Run.id.desc()).all()
    return [
        {
            "id": r.id,
            "status": r.status.value if hasattr(r.status, "value") else str(r.status),
            "created_at": r.created_at,
            "updated_at": r.updated_at,
        }
        for r in rows
    ]

# --- Models ---
@router.get("/models")
def list_models(db: Session = Depends(get_db)):
    rows = db.query(Model).order_by(Model.id.desc()).all()
    return [
        {"id": m.id, "name": m.name, "path": m.path, "created_at": m.created_at}
        for m in rows
    ]

# --- Placeholder lists (UI uses these) ---
@router.get("/workflows")
def list_workflows():
    return []

@router.get("/insights")
def get_insights():
    return []

# --------------------------
# App Generator (minimal)
# --------------------------

MODELS_ROOT = "/models"                      # mounted volume
APPS_DIR = os.path.join(MODELS_ROOT, "apps") # /models/apps

class AppGenRequest(BaseModel):
    prompt: str
    mode: Literal["app", "analyze"] = "app"
    dataset_url: Optional[str] = None

def _ensure_dirs():
    os.makedirs(APPS_DIR, exist_ok=True)

def _write_minimal_app(app_dir: str, title: str, mode: str, dataset_url: Optional[str]):
    os.makedirs(app_dir, exist_ok=True)
    # extremely small, dependency‑free page
    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 24px; background:#0b1220; color:#fff; }}
    .card {{ background: rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.1); border-radius:16px; padding:16px; }}
    .muted {{ color: rgba(255,255,255,.7); }}
    code, pre {{ background: rgba(255,255,255,.06); padding: 6px 8px; border-radius: 8px; }}
    a.button {{ display:inline-block; padding:8px 12px; border-radius:8px; background:#3b82f6; color:#fff; text-decoration:none; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <div class="card">
    <p class="muted">Mode: <b>{mode}</b></p>
    {"<p class='muted'>Dataset URL: <code>"+dataset_url+"</code></p>" if dataset_url else ""}
    <p>This is a lightweight starter app generated by FlowOpsAI.</p>
    <p class="muted">Next steps: wire data loading & add widgets.</p>
  </div>
  <script>
    // If you provided a dataset, fetch & render a tiny preview (best‑effort).
    const datasetUrl = {repr(dataset_url)};
    if (datasetUrl) {{
      fetch(datasetUrl).then(r => r.text()).then(txt => {{
        const pre = document.createElement('pre');
        pre.textContent = txt.slice(0, 2000);
        document.body.appendChild(document.createElement('br'));
        document.body.appendChild(pre);
      }}).catch(()=>{{
        const p = document.createElement('p');
        p.textContent = 'Could not fetch dataset (CORS or network).';
        document.body.appendChild(p);
      }});
    }}
  </script>
</body>
</html>
"""
    with open(os.path.join(app_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

def _zip_dir(src_dir: str, zip_path: str):
    base, _ = os.path.splitext(zip_path)
    shutil.make_archive(base, "zip", src_dir)

@router.post("/appgen/generate")
def appgen_generate(body: AppGenRequest, request: Request, db: Session = Depends(get_db)):
    if not body.prompt.strip():
        raise HTTPException(status_code=400, detail="prompt is required")

    _ensure_dirs()

    # Create a Model row first to get an ID (no new tables today)
    now = datetime.utcnow()
    model = Model(name="app-pending", path="", created_at=now)  # path to be filled after write
    db.add(model)
    db.commit()
    db.refresh(model)

    app_id = model.id
    app_name = f"app-{app_id}"
    app_dir = os.path.join(APPS_DIR, str(app_id))
    _write_minimal_app(app_dir, title=body.prompt.strip(), mode=body.mode, dataset_url=body.dataset_url)

    # Zip it
    zip_path = os.path.join(APPS_DIR, f"{app_name}.zip")
    _zip_dir(app_dir, zip_path)

    # Update model row
    model.name = app_name
    model.path = zip_path
    db.add(model)
    db.commit()

    # Build absolute URLs based on this request
    preview_url = f"/api/apps/{app_id}"
    download_url = f"/api/apps/{app_id}/download"

    return {
        "app_id": app_id,
        "name": app_name,
        "preview_url": preview_url,
        "download_url": download_url,
    }

@router.get("/appgen/apps/{app_id}")
def appgen_get(app_id: int, request: Request, db: Session = Depends(get_db)):
    m = db.get(Model, app_id)
    if not m or not (m.name or "").startswith("app-"):
        raise HTTPException(status_code=404, detail="app not found")
    preview_url = f"/api/apps/{app_id}"
    download_url = f"/api/apps/{app_id}/download"
    return {
        "app_id": app_id,
        "name": m.name,
        "preview_url": preview_url,
        "download_url": download_url,
    }

# Serve preview & download
@router.get("/apps/{app_id}")
def serve_app_index(app_id: int):
    app_index = os.path.join(APPS_DIR, str(app_id), "index.html")
    if not os.path.isfile(app_index):
        raise HTTPException(status_code=404, detail="app not found")
    return FileResponse(app_index, media_type="text/html")

@router.get("/apps/{app_id}/download")
def download_app_zip(app_id: int, db: Session = Depends(get_db)):
    m = db.get(Model, app_id)
    if not m or not (m.name or "").startswith("app-"):
        raise HTTPException(status_code=404, detail="app not found")
    zip_path = m.path or ""
    if not (zip_path and os.path.isfile(zip_path)):
        raise HTTPException(status_code=404, detail="artifact missing")
    return FileResponse(zip_path, media_type="application/zip", filename=os.path.basename(zip_path))
