from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models import RunEvent
import asyncio

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.websocket("/ws/runs/{run_id}")
async def run_events_ws(websocket: WebSocket, run_id: int, db: Session = Depends(get_db)):
    await websocket.accept()
    last_id = 0
    try:
        while True:
            events = db.query(RunEvent).filter(
                RunEvent.run_id == run_id, RunEvent.id > last_id
            ).order_by(RunEvent.id).all()
            for e in events:
                await websocket.send_json({
                    "id": e.id,
                    "ts": e.ts.isoformat(),
                    "level": e.level,
                    "title": e.title,
                    "detail": e.detail,
                })
                last_id = e.id
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        print(f"Client disconnected from run {run_id} WS")
