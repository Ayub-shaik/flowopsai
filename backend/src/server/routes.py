# backend/src/server/routes.py
from datetime import datetime
from typing import Any, Dict, List, Optional

import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.models import Model, Run, RunEvent, RunStatus, Workflow

router = APIRouter()

# -----------------------------
# DB session dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# Health
# -----------------------------
@router.get("/health")
def health():
    return {"status": "ok"}

# -----------------------------
# Feature flags (no /api here; main.py adds /api prefix)
# -----------------------------
@router.get("/features")
def get_features():
    return {
        "mcp": os.getenv("ENABLE_MCP", "0") == "1",
        "n8n": os.getenv("ENABLE_N8N", "0") == "1",
        "appgen": os.getenv("ENABLE_APPGEN", "1") == "1",
    }

# -----------------------------
# Schemas
# -----------------------------
class StartTrainRequest(BaseModel):
    prompt: str

class StepSpec(BaseModel):
    type: str
    params: Dict[str, Any] = Field(default_factory=dict)

class PipelineSpec(BaseModel):
    steps: List[StepSpec]

class CreateRunBody(BaseModel):
    pipeline: Optional[PipelineSpec] = None
    name: Optional[str] = None

# -----------------------------
# Helpers
# -----------------------------
def _enqueue_run(db: Session, *, name: Optional[str] = None, pipeline_spec: Optional[Dict[str, Any]] = None) -> Run:
    """
    Creates a Workflow (if pipeline provided), creates a Run in 'queued',
    and writes initial RunEvent.
    """
    wf_id: Optional[int] = None
    if pipeline_spec is not None:
        wf = Workflow(name=name or "ad-hoc", pipeline_spec=pipeline_spec)
        db.add(wf)
        db.flush()
        wf_id = wf.id

    run = Run(workflow_id=wf_id, status=RunStatus.queued, metrics=None)
    db.add(run)
    db.flush()

    db.add(
        RunEvent(
            run_id=run.id,
            ts=datetime.utcnow(),
            level="info",
            title="Run queued",
            detail="Awaiting agent pickup",
        )
    )
    db.commit()
    db.refresh(run)
    return run

# -----------------------------
# Chat: create a basic queued run
# (final path is /api/chat/start-train due to prefix in main.py)
# -----------------------------
@router.post("/chat/start-train")
def start_train(req: StartTrainRequest, db: Session = Depends(get_db)):
    run = _enqueue_run(db, name="chat", pipeline_spec=None)
    return {"run_id": run.id}

# -----------------------------
# Create run with optional pipeline spec
# (final path: POST /api/runs)
# -----------------------------
@router.post("/runs")
def create_run(body: CreateRunBody, db: Session = Depends(get_db)):
    pipeline_dict = body.pipeline.dict() if body.pipeline else None
    run = _enqueue_run(db, name=body.name, pipeline_spec=pipeline_dict)
    return {"run_id": run.id}

# -----------------------------
# Runs
# -----------------------------
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

# -----------------------------
# Models
# -----------------------------
@router.get("/models")
def list_models(db: Session = Depends(get_db)):
    rows = db.query(Model).order_by(Model.id.desc()).all()
    return [
        {"id": m.id, "name": m.name, "path": m.path, "created_at": m.created_at}
        for m in rows
    ]

# -----------------------------
# Placeholders so UI has data
# -----------------------------
@router.get("/workflows")
def list_workflows():
    return []

@router.get("/insights")
def get_insights():
    return []

@router.get("/insights")
def get_insights(db: Session = Depends(get_db)):
    # basic counts
    total_runs = db.query(Run).count()
    running = db.query(Run).filter(Run.status == RunStatus.running).count()
    queued = db.query(Run).filter(Run.status == RunStatus.queued).count()
    completed = db.query(Run).filter(Run.status == RunStatus.completed).count()
    failed = db.query(Run).filter(Run.status == RunStatus.failed).count()
    models_count = db.query(Model).count()

    # latest runs (10)
    latest = (
        db.query(Run)
        .order_by(Run.id.desc())
        .limit(10)
        .all()
    )
    latest_runs = [
        {
            "id": r.id,
            "status": r.status.value if hasattr(r.status, "value") else str(r.status),
            "created_at": r.created_at,
        }
        for r in latest
    ]

    return {
        "totals": {
            "runs": total_runs,
            "models": models_count,
            "queued": queued,
            "running": running,
            "completed": completed,
            "failed": failed,
        },
        "latest_runs": latest_runs,
    }
