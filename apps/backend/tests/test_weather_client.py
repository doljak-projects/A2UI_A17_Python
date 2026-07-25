import httpx
import pytest

from app.core.config import Settings
from app.services.weather_client import (
    CityNotFoundError,
    MissingOpenWeatherApiKeyError,
    OpenWeatherError,
    WeatherClient,
)

SAMPLE_PAYLOAD = {
    "name": "São Paulo",
    "main": {"temp": 24.5, "humidity": 70},
    "weather": [{"description": "céu limpo"}],
}


def make_settings(**overrides) -> Settings:
    base = {
        "llm_api_key": "sk-test",
        "llm_model": "gpt-4o-mini",
        "openweather_api_key": "ow-test-key",
    }
    base.update(overrides)
    return Settings(_env_file=None, **base)


def make_client(handler, settings=None) -> WeatherClient:
    transport = httpx.MockTransport(handler)
    return WeatherClient(
        settings=settings or make_settings(),
        http_client=httpx.Client(transport=transport),
    )


def test_get_current_weather_returns_json():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["request"] = request
        return httpx.Response(200, json=SAMPLE_PAYLOAD)

    client = make_client(handler)
    data = client.get_current_weather("São Paulo")

    request = captured["request"]
    assert data == SAMPLE_PAYLOAD
    assert request.url.path == "/data/2.5/weather"
    assert dict(request.url.params) == {
        "q": "São Paulo",
        "appid": "ow-test-key",
        "units": "metric",
        "lang": "pt_br",
    }


def test_client_requires_api_key():
    with pytest.raises(MissingOpenWeatherApiKeyError):
        WeatherClient(settings=make_settings(openweather_api_key=None))


def test_city_not_found():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"message": "city not found"})

    with pytest.raises(CityNotFoundError):
        make_client(handler).get_current_weather("Narnia")


def test_unauthorized_key():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"message": "Invalid API key"})

    with pytest.raises(OpenWeatherError, match="inválida"):
        make_client(handler).get_current_weather("São Paulo")


def test_transport_error_is_wrapped():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom")

    with pytest.raises(OpenWeatherError, match="Falha ao consultar"):
        make_client(handler).get_current_weather("São Paulo")


def test_settings_expose_openweather_config():
    settings = make_settings()
    assert settings.openweather_configured is True
    assert settings.openweather_base_url == "https://api.openweathermap.org/data/2.5"
    assert make_settings(openweather_api_key=None).openweather_configured is False
