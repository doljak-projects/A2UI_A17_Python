from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from app.schemas.weather import WeatherResult
from app.services.weather_client import WeatherApiError, WeatherClient


def get_weather(city: str, client: WeatherClient | None = None) -> WeatherResult:
    """Consulta o clima atual de uma cidade e devolve o resultado normalizado.

    Sem `client`, um `WeatherClient` é criado e fechado dentro da própria chamada.
    """
    if client is not None:
        return _to_result(client.get_current_weather(city))

    with WeatherClient() as owned_client:
        return _to_result(owned_client.get_current_weather(city))


def _to_result(payload: dict[str, Any]) -> WeatherResult:
    try:
        location = payload["location"]
        current = payload["current"]
        return WeatherResult(
            city=location["name"],
            temperature_c=current["temp_c"],
            description=current["condition"]["text"],
            humidity=current["humidity"],
        )
    except (KeyError, TypeError, ValidationError) as exc:
        raise WeatherApiError(f"Resposta inesperada da WeatherAPI: {exc}") from exc
