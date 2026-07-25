from __future__ import annotations

from types import TracebackType
from typing import Any

import httpx

from app.core.config import Settings, settings as default_settings

DEFAULT_TIMEOUT = 10.0

# Códigos de erro da WeatherAPI.com (https://www.weatherapi.com/docs/#intro-error-codes)
ERROR_NO_LOCATION_FOUND = 1006
ERROR_KEY_NOT_PROVIDED = 1002
ERROR_KEY_INVALID = 2006
ERROR_KEY_DISABLED = 2008
ERROR_QUOTA_EXCEEDED = 2007
ERROR_KEY_NO_ACCESS = 2009

INVALID_KEY_CODES = frozenset(
    {ERROR_KEY_NOT_PROVIDED, ERROR_KEY_INVALID, ERROR_KEY_DISABLED, ERROR_KEY_NO_ACCESS}
)


class WeatherApiError(RuntimeError):
    """Erro genérico na comunicação com a WeatherAPI."""


class MissingWeatherApiKeyError(WeatherApiError):
    """Levantada quando o cliente é usado sem `weather_api_key` configurada."""


class CityNotFoundError(WeatherApiError):
    """Levantada quando a cidade consultada não existe na WeatherAPI."""


class WeatherQuotaExceededError(WeatherApiError):
    """Levantada quando a cota de chamadas do plano foi excedida."""


class WeatherClient:
    """Cliente HTTP autenticado para a API da WeatherAPI.com."""

    def __init__(
        self,
        settings: Settings | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._settings = settings or default_settings
        if not self._settings.weather_configured:
            raise MissingWeatherApiKeyError(
                "weather_api_key não configurada; defina WEATHER_API_KEY no .env"
            )
        self._base_url = self._settings.weather_base_url.rstrip("/")
        self._http = http_client or httpx.Client(timeout=DEFAULT_TIMEOUT)
        self._owns_http = http_client is None

    def get_current_weather(self, city: str, lang: str = "pt") -> dict[str, Any]:
        """Retorna o clima atual da cidade, já em JSON."""
        try:
            response = self._http.get(
                f"{self._base_url}/current.json",
                params={"key": self._api_key, "q": city, "lang": lang, "aqi": "no"},
            )
        except httpx.HTTPError as exc:
            raise WeatherApiError(f"Falha ao consultar a WeatherAPI: {exc}") from exc

        if response.is_error:
            self._raise_for_error(response, city)

        return response.json()

    def _raise_for_error(self, response: httpx.Response, city: str) -> None:
        code, message = self._extract_error(response)

        if code == ERROR_NO_LOCATION_FOUND:
            raise CityNotFoundError(f"Cidade '{city}' não encontrada")
        if code in INVALID_KEY_CODES:
            raise WeatherApiError(f"Chave da WeatherAPI inválida ou não autorizada: {message}")
        if code == ERROR_QUOTA_EXCEEDED:
            raise WeatherQuotaExceededError("Cota de chamadas da WeatherAPI excedida")

        raise WeatherApiError(f"WeatherAPI retornou {response.status_code}: {message}")

    @staticmethod
    def _extract_error(response: httpx.Response) -> tuple[int | None, str]:
        try:
            error = response.json().get("error", {})
        except ValueError:
            return None, response.text
        return error.get("code"), error.get("message", response.text)

    @property
    def _api_key(self) -> str:
        assert self._settings.weather_api_key is not None  # garantido no __init__
        return self._settings.weather_api_key.get_secret_value()

    def close(self) -> None:
        if self._owns_http:
            self._http.close()

    def __enter__(self) -> WeatherClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()
