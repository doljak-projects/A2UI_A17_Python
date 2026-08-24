"""Geração determinística de mensagens A2UI para os cards de clima.

Dois cards separados — tempo e umidade — para o agente escolher um por turno
conforme o contexto da pergunta. Espelha `createWeatherCard()`/`createHumidityCard()`
do frontend (`a2ui-weather-card.ts`).
"""

from __future__ import annotations

from typing import Any

from app.schemas.weather import WeatherResult

A2uiMessage = dict[str, Any]


def create_weather_card(
    surface_id: str,
    catalog_id: str,
    data: WeatherResult,
) -> list[A2uiMessage]:
    """Card de tempo: `TemperatureHero` como raiz (cidade + temperatura)."""
    return _surface_messages(
        surface_id,
        catalog_id,
        data,
        [
            {
                "id": "root",
                "component": "TemperatureHero",
                "city": {"path": "/city"},
                "temperature": {"path": "/temperature_c"},
                "description": {"path": "/description"},
            }
        ],
    )


def create_humidity_card(
    surface_id: str,
    catalog_id: str,
    data: WeatherResult,
) -> list[A2uiMessage]:
    """Card de umidade: `HumidityGauge` como raiz (cidade + umidade)."""
    return _surface_messages(
        surface_id,
        catalog_id,
        data,
        [
            {
                "id": "root",
                "component": "HumidityGauge",
                "city": {"path": "/city"},
                "humidity": {"path": "/humidity"},
            }
        ],
    )


def _surface_messages(
    surface_id: str,
    catalog_id: str,
    data: WeatherResult,
    components: list[dict[str, Any]],
) -> list[A2uiMessage]:
    return [
        {
            "version": "v0.9",
            "createSurface": {"surfaceId": surface_id, "catalogId": catalog_id},
        },
        {
            "version": "v0.9",
            "updateComponents": {
                "surfaceId": surface_id,
                "components": components,
            },
        },
        {
            "version": "v0.9",
            "updateDataModel": {
                "surfaceId": surface_id,
                "value": data.model_dump(),
            },
        },
    ]
