import httpx
import pytest

from app.core.config import Settings
from app.schemas.weather import WeatherResult
from app.services.weather import get_weather
from app.services.weather_client import CityNotFoundError, WeatherApiError, WeatherClient
from app.tools import execute_tool, get_tools_schema, registry
from app.tools.weather import GetWeatherTool

SAMPLE_PAYLOAD = {
    "location": {"name": "Sao Paulo", "region": "Sao Paulo", "country": "Brazil"},
    "current": {
        "temp_c": 18.1,
        "humidity": 77,
        "condition": {"text": "Parcialmente nublado", "code": 1003},
    },
}


def make_settings(**overrides) -> Settings:
    base = {
        "llm_api_key": "sk-test",
        "llm_model": "gpt-4o-mini",
        "weather_api_key": "weather-test-key",
    }
    base.update(overrides)
    return Settings(_env_file=None, **base)


def make_client(handler) -> WeatherClient:
    return WeatherClient(
        settings=make_settings(),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )


def json_handler(payload, status: int = 200):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json=payload)

    return handler


@pytest.fixture
def mock_weather_api(monkeypatch):
    """Faz `get_weather` criar um WeatherClient apontado para um transporte falso."""

    def install(handler):
        monkeypatch.setattr(
            "app.services.weather.WeatherClient",
            lambda: make_client(handler),
        )

    return install


def test_get_weather_normalizes_payload():
    result = get_weather("Sao Paulo", client=make_client(json_handler(SAMPLE_PAYLOAD)))

    assert result == WeatherResult(
        city="Sao Paulo",
        temperature_c=18.1,
        description="Parcialmente nublado",
        humidity=77,
    )


def test_get_weather_creates_own_client_when_omitted(mock_weather_api):
    mock_weather_api(json_handler(SAMPLE_PAYLOAD))

    assert get_weather("Sao Paulo").city == "Sao Paulo"


def test_get_weather_propagates_city_not_found():
    handler = json_handler({"error": {"code": 1006, "message": "No matching location"}}, 400)

    with pytest.raises(CityNotFoundError, match="Narnia"):
        get_weather("Narnia", client=make_client(handler))


def test_malformed_payload_raises_weather_api_error():
    handler = json_handler({"location": {"name": "Sao Paulo"}})

    with pytest.raises(WeatherApiError, match="Resposta inesperada"):
        get_weather("Sao Paulo", client=make_client(handler))


def test_tool_schema_declares_city_argument():
    schema = GetWeatherTool().schema()

    assert schema["name"] == "get_weather"
    assert schema["input_schema"]["required"] == ["city"]
    assert schema["input_schema"]["properties"]["city"]["type"] == "string"


def test_tool_registered_in_default_registry():
    assert "get_weather" in registry
    assert "get_weather" in [tool["name"] for tool in get_tools_schema()]


def test_execute_tool_returns_serializable_dict(mock_weather_api):
    mock_weather_api(json_handler(SAMPLE_PAYLOAD))

    assert execute_tool("get_weather", {"city": "Sao Paulo"}) == {
        "city": "Sao Paulo",
        "temperature_c": 18.1,
        "description": "Parcialmente nublado",
        "humidity": 77,
    }
