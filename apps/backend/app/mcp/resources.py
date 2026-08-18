"""Recurso HTML do widget MCP Apps de clima (issues #81/#83)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from app.agui.a2ui_constants import WEATHER_MCP_RESOURCE_URI

_WIDGET_PATH = Path(__file__).resolve().parent / "assets" / "weather_card.html"


@lru_cache(maxsize=1)
def load_weather_app_html() -> str:
    return _WIDGET_PATH.read_text(encoding="utf-8")


def read_weather_app_resource(uri: str) -> dict[str, str]:
    if uri != WEATHER_MCP_RESOURCE_URI:
        raise KeyError(f"Recurso desconhecido: {uri}")
    return {
        "uri": uri,
        "mimeType": "text/html",
        "text": load_weather_app_html(),
        "_meta": {
            "ui": {
                "csp": {
                    "resourceDomains": [],
                },
            },
        },
    }
