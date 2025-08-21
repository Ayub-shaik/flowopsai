# backend/src/server/integrations.py
import os
from fastapi import APIRouter

router = APIRouter(prefix="/integrations", tags=["integrations"])

@router.get("/status")
def status():
    """
    Minimal surface to tell the UI what is enabled and where things live.
    We don’t hit n8n/MCP; we just report env + derived URLs.
    """
    enable_mcp = os.getenv("ENABLE_MCP", "0") == "1"
    enable_n8n = os.getenv("ENABLE_N8N", "0") == "1"

    # If you later run n8n in docker-compose, we’ll proxy it via /n8n
    # so the UI can iframe it at `${location.origin}/n8n/`.
    return {
        "mcp": {
            "enabled": enable_mcp,
            "mode": os.getenv("MCP_MODE", "local"),   # local|remote
            "server_url": os.getenv("MCP_SERVER_URL", None),
        },
        "n8n": {
            "enabled": enable_n8n,
            "ui_url_hint": "/n8n/",  # front-end will use this when enabled
        },
    }
