import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.server import routes  # absolute import within package
from src.database import engine, Base

# Ensure tables exist (Alembic is preferred, but this helps first boot)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FlowOpsAI Backend")

# If you access API directly from a different origin in dev, enable CORS (proxy via Nginx recommended)
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

@app.get("/")
def root():
    return {"message": "Welcome to FlowOpsAI backend!"}
