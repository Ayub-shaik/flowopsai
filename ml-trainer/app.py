# ml-trainer/app.py
import os
import time
import json
import requests
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="FlowOpsAI Trainer")

BACKEND_BASE = os.getenv("BACKEND_BASE_URL", "http://backend-server:8181")
POST_EVENT_URL = lambda run_id: f"{BACKEND_BASE}/api/runs/{run_id}/events"
PUT_METRICS_URL = lambda run_id: f"{BACKEND_BASE}/api/runs/{run_id}/metrics"
COMPLETE_URL = lambda run_id: f"{BACKEND_BASE}/api/runs/{run_id}/complete"

class StartOut(BaseModel):
    ok: bool = True

def post_event(run_id: int, level: str, title: str, detail: str = ""):
    payload = {"level": level, "title": title, "detail": detail}
    r = requests.post(POST_EVENT_URL(run_id), json=payload, timeout=10)
    r.raise_for_status()

def put_metrics(run_id: int, metrics: dict):
    r = requests.put(PUT_METRICS_URL(run_id), json={"metrics": metrics}, timeout=10)
    r.raise_for_status()

@app.get("/")
def root():
    return {"status": "trainer ok"}

@app.post("/start/{run_id}", response_model=StartOut)
def start_training(run_id: int):
    # Notify: started
    post_event(run_id, "info", "Run started", "Trainer picked up run")

    # Fake steps & rolling metrics
    for i in range(1, 4):
        time.sleep(2)
        # pretend metric improves each step
        metrics = {
            "step": i,
            "accuracy": round(0.70 + i * 0.08, 3),
            "loss": round(0.9 - i * 0.2, 3),
        }
        put_metrics(run_id, metrics)
        post_event(run_id, "info", f"Step {i}", f"Trainer finished step {i}")

    # Simulate writing a tiny “artifact”
    models_dir = "/models"
    os.makedirs(models_dir, exist_ok=True)
    artifact_path = os.path.join(models_dir, f"run-{run_id}", "model.bin")
    os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
    with open(artifact_path, "wb") as f:
        f.write(b"\x00\x01\x02\x03")

    # Notify: completed + register model
    post_event(run_id, "info", "Run completed", "All steps done in trainer")
    r = requests.post(
        COMPLETE_URL(run_id),
        json={"model_name": f"model-run-{run_id}", "model_path": artifact_path},
        timeout=10,
    )
    r.raise_for_status()

    return StartOut()
