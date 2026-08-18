"""Geração determinística de mensagens A2UI para o card de clima (issue #72).

Espelha `createWeatherCard()`/`refreshWeatherCardData()` do frontend
(`a2ui-weather-card.ts`, issues #54/#55), agora do lado do backend, pra que o
agente monte as mesmas operações A2UI que seriam construídas manualmente na
rota de demo isolada `/a2ui-test`.
"""

from __future__ import annotations

from typing import Any

from app.agui.a2ui_constants import REFRESH_WEATHER_ACTION
from app.schemas.weather import WeatherResult

A2uiMessage = dict[str, Any]


def create_weather_card(
    surface_id: str,
    catalog_id: str,
    data: WeatherResult,
    *,
    use_humidity_gauge: bool = False,
) -> list[A2uiMessage]:
    """Monta o ciclo `createSurface`/`updateComponents`/`updateDataModel`.

    `use_humidity_gauge` desligado por padrão: o catálogo customizado com o
    componente `HumidityGauge` só é registrado na issue #76 — até lá, o campo
    de umidade usa um `Text` simples, igual ao card original da issue #54.
    """
    humidity_component: dict[str, Any]
    if use_humidity_gauge:
        humidity_component = {
            "id": "card-humidity",
            "component": "HumidityGauge",
            "humidity": {"path": "/humidity"},
        }
    else:
        humidity_component = {
            "id": "card-humidity",
            "component": "Text",
            "variant": "caption",
            "text": {"path": "/humidity"},
        }

    return [
        {
            "version": "v0.9",
            "createSurface": {"surfaceId": surface_id, "catalogId": catalog_id},
        },
        {
            "version": "v0.9",
            "updateComponents": {
                "surfaceId": surface_id,
                "components": [
                    {"id": "root", "component": "Card", "child": "card-column"},
                    {
                        "id": "card-column",
                        "component": "Column",
                        "children": [
                            "card-city",
                            "card-temperature",
                            "card-description",
                            "card-humidity",
                            "refresh-button",
                        ],
                    },
                    {
                        "id": "card-city",
                        "component": "Text",
                        "variant": "h3",
                        "text": {"path": "/city"},
                    },
                    {
                        "id": "card-temperature",
                        "component": "Text",
                        "variant": "body",
                        "text": {"path": "/temperature_c"},
                    },
                    {
                        "id": "card-description",
                        "component": "Text",
                        "variant": "body",
                        "text": {"path": "/description"},
                    },
                    humidity_component,
                    {
                        "id": "refresh-button-label",
                        "component": "Text",
                        "variant": "body",
                        "text": "Atualizar",
                    },
                    {
                        "id": "refresh-button",
                        "component": "Button",
                        "child": "refresh-button-label",
                        "action": {"event": {"name": REFRESH_WEATHER_ACTION}},
                    },
                ],
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
