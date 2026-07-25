import httpx
import pytest

from app.core.config import Settings
from app.services.weather_client import (
    CityNotFoundError,
    MissingWeatherApiKeyError,
    WeatherApiError,
    WeatherClient,
    WeatherQuotaExceededError,
)

SAMPLE_PAYLOAD = {
    "location": {"name": "Sao Paulo", "region": "Sao Paulo", "country": "Brazil"},
    "current": {
        "temp_c": 18.0,
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


def make_client(handler, settings=None) -> WeatherClient:
    return WeatherClient(
        settings=settings or make_settings(),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )


def error_handler(status: int, code: int, message: str = "erro"):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json={"error": {"code": code, "message": message}})

    return handler


def test_get_current_weather_returns_json():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["request"] = request
        return httpx.Response(200, json=SAMPLE_PAYLOAD)

    data = make_client(handler).get_current_weather("Sao Paulo")
    request = captured["request"]

    assert data == SAMPLE_PAYLOAD
    assert request.url.path == "/v1/current.json"
    assert dict(request.url.params) == {
        "key": "weather-test-key",
        "q": "Sao Paulo",
        "lang": "pt",
        "aqi": "no",
    }


def test_client_requires_api_key():
    with pytest.raises(MissingWeatherApiKeyError):
        WeatherClient(settings=make_settings(weather_api_key=None))


def test_city_not_found_maps_error_code_1006():
    handler = error_handler(400, 1006, "No matching location found.")
    with pytest.raises(CityNotFoundError, match="Narnia"):
        make_client(handler).get_current_weather("Narnia")


@pytest.mark.parametrize("code", [1002, 2006, 2008, 2009])
def test_invalid_key_codes(code):
    handler = error_handler(401, code, "API key is invalid.")
    with pytest.raises(WeatherApiError, match="inválida"):
        make_client(handler).get_current_weather("Sao Paulo")


def test_quota_exceeded():
    handler = error_handler(403, 2007, "quota exceeded")
    with pytest.raises(WeatherQuotaExceededError):
        make_client(handler).get_current_weather("Sao Paulo")


def test_unknown_error_is_wrapped():
    handler = error_handler(500, 9999, "Internal application error.")
    with pytest.raises(WeatherApiError, match="500"):
        make_client(handler).get_current_weather("Sao Paulo")


def test_transport_error_is_wrapped():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom")

    with pytest.raises(WeatherApiError, match="Falha ao consultar"):
        make_client(handler).get_current_weather("Sao Paulo")


def test_settings_expose_weather_config():
    settings = make_settings()
    assert settings.weather_configured is True
    assert settings.weather_base_url == "https://api.weatherapi.com/v1"
    assert make_settings(weather_api_key=None).weather_configured is False
