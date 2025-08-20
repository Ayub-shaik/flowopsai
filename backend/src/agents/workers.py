import time
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Run, RunStatus, RunEvent
from src.database import DATABASE_URL

# Setup DB session for agent loop
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def now_utc():
    return datetime.now(timezone.utc)

def process_run(run: Run, db: Session):
    print(f"Processing run {run.id}...")
    # Mark as running
    run.status = RunStatus.running
    db.add(RunEvent(run_id=run.id, ts=now_utc(), level="info",
                    title="Run started", detail="Agent picked up run"))
    db.commit()

    # Fake training steps
    for i in range(1, 4):
        time.sleep(3)
        db.add(RunEvent(run_id=run.id, ts=now_utc(), level="info",
                        title=f"Step {i}", detail=f"Completed fake step {i}"))
        db.commit()

    # Mark as completed
    run.status = RunStatus.completed
    db.add(RunEvent(run_id=run.id, ts=now_utc(), level="info",
                    title="Run completed", detail="All steps done"))
    db.commit()
    print(f"Run {run.id} completed.")

def run_worker():
    print("Agent worker loop starting...")
    while True:
        with SessionLocal() as db:
            queued = db.query(Run).filter(Run.status == RunStatus.queued).all()
            for run in queued:
                process_run(run, db)
        time.sleep(5)
