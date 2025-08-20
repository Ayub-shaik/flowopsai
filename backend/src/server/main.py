import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.server import routes, ws
from src.database import engine, Base

# Ensure tables exist (Alembic is preferred, but this helps first boot)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FlowOpsAI Backend")

# Enable CORS if needed
if os.getenv("ENABLE_CORS", "0") == "1":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# include API routes and WS
app.include_router(routes.router)   
app.include_router(ws.router)

@app.get("/")
def root():
    return {"message": "Welcome to FlowOpsAI backend!"}
