"""DSL compacta para mini-dashboard de clima (issues #78/#79)."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.agui.a2ui_constants import WEATHER_CATALOG_ID
from app.schemas.weather import WeatherResult

TileType = Literal["currentWeather"]


class WeatherDashboardTile(BaseModel):
    type: TileType = "currentWeather"
    city: str = Field(min_length=1)


class WeatherDashboardDsl(BaseModel):
    """Formato restrito que o agente/LLM produziria em vez de markup A2UI completo."""

    tiles: list[WeatherDashboardTile] = Field(min_length=1)


def dsl_from_cities(cities: list[str]) -> WeatherDashboardDsl:
    return WeatherDashboardDsl(
        tiles=[WeatherDashboardTile(city=city) for city in cities],
    )


def hash_dsl(dsl: WeatherDashboardDsl) -> str:
    payload = json.dumps(dsl.model_dump(), ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def build_dashboard_components(surface_id: str, dsl: WeatherDashboardDsl) -> list[dict[str, Any]]:
    """Converte a DSL numa árvore achatada `updateComponents` (issue #79)."""
    column_children: list[str] = []
    components: list[dict[str, Any]] = [
        {"id": "root", "component": "Card", "child": "dashboard-column"},
        {
            "id": "dashboard-column",
            "component": "Column",
            "children": column_children,
        },
    ]

    for index, tile in enumerate(dsl.tiles):
        prefix = f"tile-{index}"
        column_children.extend(
            [
                f"{prefix}-city",
                f"{prefix}-temperature",
                f"{prefix}-description",
                f"{prefix}-humidity",
            ],
        )
        base_path = f"/tiles/{index}"
        components.extend(
            [
                {
                    "id": f"{prefix}-city",
                    "component": "Text",
                    "variant": "h3",
                    "text": {"path": f"{base_path}/city"},
                },
                {
                    "id": f"{prefix}-temperature",
                    "component": "Text",
                    "variant": "body",
                    "text": {"path": f"{base_path}/temperature_c"},
                },
                {
                    "id": f"{prefix}-description",
                    "component": "Text",
                    "variant": "body",
                    "text": {"path": f"{base_path}/description"},
                },
                {
                    "id": f"{prefix}-humidity",
                    "component": "Text",
                    "variant": "caption",
                    "text": {"path": f"{base_path}/humidity"},
                },
            ],
        )

    return components


def build_dashboard_data_model(weather_by_tile: list[WeatherResult]) -> dict[str, Any]:
    return {"tiles": [result.model_dump() for result in weather_by_tile]}


def build_dashboard_messages(
    surface_id: str,
    dsl: WeatherDashboardDsl,
    weather_by_tile: list[WeatherResult],
) -> list[dict[str, Any]]:
    return [
        {
            "version": "v0.9",
            "createSurface": {"surfaceId": surface_id, "catalogId": WEATHER_CATALOG_ID},
        },
        {
            "version": "v0.9",
            "updateComponents": {
                "surfaceId": surface_id,
                "components": build_dashboard_components(surface_id, dsl),
            },
        },
        {
            "version": "v0.9",
            "updateDataModel": {
                "surfaceId": surface_id,
                "value": build_dashboard_data_model(weather_by_tile),
            },
        },
    ]
