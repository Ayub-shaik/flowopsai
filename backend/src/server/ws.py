from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from datetime import timezone
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models import RunEvent

router = APIRouter()

@router.websocket("/ws/runs/{run_id}")
async def ws_run_events(websocket: WebSocket, run_id: int):
    # Accept without extra checks (nginx handles origin); tighten later if needed
    await websocket.accept()
    print(f"WebSocket connected for run {run_id}")

    last_id = 0
    try:
        while True:
            await asyncio.sleep(2)  # poll every 2s
            with SessionLocal() as db:
                new_events = (
                    db.query(RunEvent)
                    .filter(RunEvent.run_id == run_id, RunEvent.id > last_id)
                    .order_by(RunEvent.id.asc())
                    .all()
                )
                for ev in new_events:
                    # DB stores naive UTC; make it explicit for clients
                    ts = ev.ts.replace(tzinfo=timezone.utc).isoformat()
                    await websocket.send_json({
                        "id": ev.id,
                        "ts": ts,
                        "level": ev.level,
                        "title": ev.title,
                        "detail": ev.detail,
                    })
                    last_id = ev.id
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for run {run_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass
