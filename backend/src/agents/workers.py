import time
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import urllib.request

from src.models import Run, RunStatus, RunEvent
from src.database import DATABASE_URL

# Setup DB session for agent loop
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def now_utc():
    return datetime.now(timezone.utc)

def _trigger_trainer(run_id: int):
    """
    Fire-and-forget HTTP POST to the trainer service to start work.
    Uses stdlib urllib to avoid extra deps.
    """
    url = f"http://trainer:8090/start/{run_id}"
    req = urllib.request.Request(url=url, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        # consume response to avoid broken pipe on server
        _ = resp.read()

def process_run(run: Run, db: Session):
    print(f"Processing run {run.id}...")
    # Mark as running + initial event
    run.status = RunStatus.running
    db.add(RunEvent(run_id=run.id, ts=now_utc(), level="info",
                    title="Run started", detail="Agent picked up run"))
    db.commit()

    # Trigger trainer; on failure, mark run failed and emit error event
    try:
        _trigger_trainer(run.id)
        db.add(RunEvent(run_id=run.id, ts=now_utc(), level="info",
                        title="Trainer invoked", detail="Trainer accepted job"))
        db.commit()
    except Exception as e:
        run.status = RunStatus.failed
        db.add(RunEvent(run_id=run.id, ts=now_utc(), level="error",
                        title="Trainer trigger failed", detail=str(e)))
        db.commit()
        print(f"Trainer trigger failed for run {run.id}: {e}")
        return

    # Note:
    # From here, we let the trainer post granular events and final completion.
    # The agent doesn't synthesize steps anymore.

    print(f"Run {run.id} delegated to trainer.")

def run_worker():
    print("Agent worker loop starting...")
    while True:
        with SessionLocal() as db:
            queued = db.query(Run).filter(Run.status == RunStatus.queued).all()
            for run in queued:
                process_run(run, db)
        time.sleep(5)
