# backend/src/server/routes.py
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.models import Run, RunStatus, RunEvent, Workflow, Model

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def utcnow():
    return datetime.now(timezone.utc)

# ---------------- Schemas ----------------

class HealthOut(BaseModel):
    status: str = "ok"

class StartTrainIn(BaseModel):
    prompt: str = Field(..., description="User free-text prompting the training job")

class StartTrainOut(BaseModel):
    run_id: int

class RunEventIn(BaseModel):
    level: str = Field("info", pattern="^(info|warn|error)$")
    title: str
    detail: Optional[str] = None
    ts: Optional[datetime] = None

class ModelOut(BaseModel):
    id: int
    name: str
    path: str
    created_at: datetime

class WorkflowOut(BaseModel):
    id: int
    name: str
    pipeline_spec: Optional[dict] = None
    created_at: datetime

class RunOut(BaseModel):
    id: int
    status: RunStatus
    metrics: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    workflow_id: Optional[int] = None

class MetricsIn(BaseModel):
    metrics: Dict[str, Any]

class CompleteIn(BaseModel):
    model_name: str = "sample-model"
    model_path: str = "/models/sample/model.bin"

# --------------- Endpoints ----------------

@router.get("/api/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut()

@router.get("/api/workflows", response_model=List[WorkflowOut])
def list_workflows(db: Session = Depends(get_db)):
    rows = db.query(Workflow).order_by(Workflow.id.asc()).all()
    return [
        WorkflowOut(
            id=w.id, name=w.name, pipeline_spec=w.pipeline_spec, created_at=w.created_at
        )
        for w in rows
    ]

@router.get("/api/models", response_model=List[ModelOut])
def list_models(db: Session = Depends(get_db)):
    rows = db.query(Model).order_by(Model.id.desc()).all()
    return [
        ModelOut(id=m.id, name=m.name, path=m.path, created_at=m.created_at)
        for m in rows
    ]

@router.post("/api/chat/start-train", response_model=StartTrainOut)
def start_train(body: StartTrainIn, db: Session = Depends(get_db)) -> StartTrainOut:
    wf = db.query(Workflow).order_by(Workflow.id.asc()).first()
    run = Run(
        workflow_id=wf.id if wf else None,
        status=RunStatus.queued,
        metrics=None,
        created_at=utcnow(),
        updated_at=utcnow(),
    )
    db.add(run)
    db.flush()  # assign run.id

    db.add(
        RunEvent(
            run_id=run.id,
            ts=utcnow(),
            level="info",
            title="Run queued",
            detail="Awaiting agent pickup",
        )
    )
    db.commit()
    return StartTrainOut(run_id=run.id)

# 🔎 Read one run (status + metrics)
@router.get("/api/runs/{run_id}", response_model=RunOut)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunOut(
        id=run.id,
        status=run.status,
        metrics=run.metrics,
        created_at=run.created_at,
        updated_at=run.updated_at,
        workflow_id=run.workflow_id,
    )

# 🔥 Trainer posts events here (unchanged)
@router.post("/api/runs/{run_id}/events")
def post_run_event(run_id: int, ev: RunEventIn, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    db.add(
        RunEvent(
            run_id=run.id,
            ts=ev.ts or utcnow(),
            level=ev.level,
            title=ev.title,
            detail=ev.detail,
        )
    )
    if ev.title.lower().startswith("run started"):
        run.status = RunStatus.running
        run.updated_at = utcnow()
    elif ev.title.lower().startswith("run completed"):
        run.status = RunStatus.completed
        run.updated_at = utcnow()

    db.commit()
    return {"ok": True}

# 🧮 Trainer updates metrics JSON here
@router.put("/api/runs/{run_id}/metrics")
def put_run_metrics(run_id: int, body: MetricsIn, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    run.metrics = body.metrics
    run.updated_at = utcnow()
    db.commit()
    return {"ok": True}

@router.post("/api/runs/{run_id}/complete")
def complete_run(run_id: int, body: CompleteIn, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    db.add(
        RunEvent(
            run_id=run.id,
            ts=utcnow(),
            level="info",
            title="Run completed",
            detail="Finalized by trainer",
        )
    )
    run.status = RunStatus.completed
    run.updated_at = utcnow()

    model = Model(name=body.model_name, path=body.model_path, created_at=utcnow())
    db.add(model)
    db.commit()
    return {"ok": True, "model_id": model.id}

# 📥 Model artifact download
@router.get("/api/models/{model_id}/download")
def download_model(model_id: int, db: Session = Depends(get_db)):
    m = db.query(Model).filter(Model.id == model_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Model not found")
    if not os.path.isfile(m.path):
        raise HTTPException(status_code=404, detail="Artifact missing on disk")
    filename = os.path.basename(m.path)
    return FileResponse(m.path, media_type="application/octet-stream", filename=filename)
