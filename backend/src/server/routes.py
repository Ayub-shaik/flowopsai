from fastapi import APIRouter
from ..mlops.trainer import train_model_stub
from ..mlops.evaluator import evaluate_model_stub

router = APIRouter()

@router.get("/ping")
def ping():
    return {"message": "pong"}

@router.post("/train")
def train_model():
    result = train_model_stub()
    return {"status": "training started", "result": result}

@router.get("/evaluate")
def evaluate_model():
    result = evaluate_model_stub()
    return {"status": "evaluation complete", "result": result}
