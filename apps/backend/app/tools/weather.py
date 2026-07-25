from __future__ import annotations

from typing import Any

from app.services.weather import get_weather
from app.tools.base import Tool
from app.tools.registry import registry


class GetWeatherTool(Tool):
    """Expõe o clima atual de uma cidade como tool chamável pelo LLM."""

    name = "get_weather"
    description = (
        "Consulta as condições climáticas atuais de uma cidade. "
        "Retorna temperatura em graus Celsius, descrição do tempo e umidade relativa."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "Nome da cidade a consultar, ex.: 'São Paulo' ou 'Lisboa'",
            }
        },
        "required": ["city"],
        "additionalProperties": False,
    }

    def execute(self, arguments: dict[str, Any]) -> Any:
        # O cliente HTTP é criado por chamada para que registrar a tool não exija
        # que a WEATHER_API_KEY esteja configurada no boot da aplicação.
        return get_weather(arguments["city"]).model_dump()


def register_weather_tools() -> None:
    """Registra as tools de clima no registry padrão (idempotente)."""
    if "get_weather" not in registry:
        registry.register(GetWeatherTool())
