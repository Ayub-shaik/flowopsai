from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.database import get_db
from src import models as dbm

router = APIRouter(prefix="/api", tags=["api"])

@router.get("/health")
def health():
    return {"status": "ok"}

# ---- Models ----
@router.get("/models")
def list_models(db: Session = Depends(get_db)):
    rows = db.query(dbm.Model).order_by(dbm.Model.id.desc()).all()
    return [{"id": r.id, "name": r.name, "path": r.path, "created_at": r.created_at} for r in rows]

# ---- Workflows ----
@router.get("/workflows")
def list_workflows(db: Session = Depends(get_db)):
    rows = db.query(dbm.Workflow).order_by(dbm.Workflow.id.desc()).all()
    return [{"id": w.id, "name": w.name, "pipeline_spec": w.pipeline_spec, "created_at": w.created_at} for w in rows]

@router.post("/workflows/new")
def create_workflow(name: Optional[str] = None, db: Session = Depends(get_db)):
    name = name or "Sample Workflow"
    wf = dbm.Workflow(name=name, pipeline_spec={"stages": ["profile", "train", "evaluate", "register"]})
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return {"id": wf.id, "name": wf.name}

# ---- Chat → start train ----
@router.post("/chat/start-train")
def start_train(workflow_id: Optional[int] = None, db: Session = Depends(get_db)):
    run = dbm.Run(workflow_id=workflow_id, status=dbm.RunStatus.queued)
    db.add(run)
    db.commit()
    db.refresh(run)

    # Seed initial event so UI has something to show
    ev = dbm.RunEvent(run_id=run.id, level="info", title="Run queued", detail="Awaiting agent pickup")
    db.add(ev)
    db.commit()

    return {"run_id": run.id, "status": run.status}

@router.get("/runs/{run_id}")
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.get(dbm.Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    events = db.query(dbm.RunEvent).filter(dbm.RunEvent.run_id == run_id).order_by(dbm.RunEvent.id.asc()).all()
    return {
        "id": run.id,
        "status": run.status,
        "metrics": run.metrics,
        "workflow_id": run.workflow_id,
        "events": [
            {"id": e.id, "ts": e.ts.isoformat(), "level": e.level, "title": e.title, "detail": e.detail}
            for e in events
        ],
    }

# ---- Insights ----
@router.get("/insights")
def insights(db: Session = Depends(get_db)):
    total_runs = db.query(func.count(dbm.Run.id)).scalar() or 0
    completed = db.query(func.count(dbm.Run.id)).filter(dbm.Run.status == dbm.RunStatus.completed).scalar() or 0
    success_rate = (completed / total_runs * 100.0) if total_runs else 0.0
    total_models = db.query(func.count(dbm.Model.id)).scalar() or 0
    return {"runs_total": total_runs, "success_rate": round(success_rate, 2), "models_total": total_models}

# ---- Minimal WS for /ws/runs/{id} ----
# This WS sends current events on connect and keeps the socket open with heartbeat.
@router.websocket("/ws/runs/{run_id}")
async def ws_run_events(websocket: WebSocket, run_id: int, db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        # send existing events once
        events = db.query(dbm.RunEvent).filter(dbm.RunEvent.run_id == run_id).order_by(dbm.RunEvent.id.asc()).all()
        payload = [
            {"id": e.id, "ts": e.ts.isoformat(), "level": e.level, "title": e.title, "detail": e.detail}
            for e in events
        ]
        await websocket.send_json({"type": "snapshot", "events": payload})
        # keep alive; agent will append events which UI can refresh via polling for now
        while True:
            await websocket.send_json({"type": "heartbeat"})
            await asyncio.sleep(15)
    except WebSocketDisconnect:
        return
    except Exception as e:
        # best-effort error report over WS
        try:
            await websocket.send_json({"type": "error", "detail": str(e)})
        except Exception:
            pass
        await websocket.close()
