from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.mcp.resources import load_weather_app_html

router = APIRouter()


@router.get("/mcp-apps/weather-card", response_class=HTMLResponse)
def weather_mcp_app_html() -> str:
    """Serve o widget HTML para demos isoladas de MCP Apps (issues #82/#83)."""
    return load_weather_app_html()
