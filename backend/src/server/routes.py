from fastapi import APIRouter
# use absolute import to sibling package
from mlops.trainer import train_model_stub  # adjust to your actual function names

router = APIRouter(prefix="/api", tags=["api"])

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/train")
def trigger_train():
    # simple stub; call your real training orchestration
    result = train_model_stub()
    return {"message": "training started", "result": result}
