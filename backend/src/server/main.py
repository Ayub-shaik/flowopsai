# backend/src/server/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.server import routes, ws
from src.server import integrations  # <-- add this
from src.server.apps_routes import router as apps_router


app = FastAPI(title="FlowOpsAI Backend")

# Optional CORS in dev (handy if you ever run vite dev server directly)
if os.getenv("ENABLE_CORS", "0") == "1":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# REST under /api
app.include_router(routes.router, prefix="/api")

# WebSocket WITHOUT /api (nginx proxies /ws to backend)
app.include_router(ws.router)

app.include_router(integrations.router, prefix="/api") 
app.include_router(apps_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Welcome to FlowOpsAI backend!"}
