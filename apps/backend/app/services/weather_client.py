from __future__ import annotations

from types import TracebackType
from typing import Any

import httpx

from app.core.config import Settings, settings as default_settings

DEFAULT_TIMEOUT = 10.0


class OpenWeatherError(RuntimeError):
    """Erro genérico na comunicação com a OpenWeatherMap."""


class MissingOpenWeatherApiKeyError(OpenWeatherError):
    """Levantada quando o cliente é usado sem `openweather_api_key` configurada."""


class CityNotFoundError(OpenWeatherError):
    """Levantada quando a cidade consultada não existe na OpenWeatherMap."""


class WeatherClient:
    """Cliente HTTP autenticado para a API da OpenWeatherMap."""

    def __init__(
        self,
        settings: Settings | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._settings = settings or default_settings
        if not self._settings.openweather_configured:
            raise MissingOpenWeatherApiKeyError(
                "openweather_api_key não configurada; defina OPENWEATHER_API_KEY no .env"
            )
        self._base_url = self._settings.openweather_base_url.rstrip("/")
        self._http = http_client or httpx.Client(timeout=DEFAULT_TIMEOUT)
        self._owns_http = http_client is None

    def get_current_weather(
        self, city: str, units: str = "metric", lang: str = "pt_br"
    ) -> dict[str, Any]:
        """Retorna o clima atual da cidade, já em JSON."""
        try:
            response = self._http.get(
                f"{self._base_url}/weather",
                params={
                    "q": city,
                    "appid": self._api_key,
                    "units": units,
                    "lang": lang,
                },
            )
        except httpx.HTTPError as exc:
            raise OpenWeatherError(f"Falha ao consultar a OpenWeatherMap: {exc}") from exc

        if response.status_code == httpx.codes.NOT_FOUND:
            raise CityNotFoundError(f"Cidade '{city}' não encontrada")
        if response.status_code == httpx.codes.UNAUTHORIZED:
            raise OpenWeatherError("Chave da OpenWeatherMap inválida ou não autorizada")
        if response.is_error:
            raise OpenWeatherError(
                f"OpenWeatherMap retornou {response.status_code}: {response.text}"
            )

        return response.json()

    @property
    def _api_key(self) -> str:
        assert self._settings.openweather_api_key is not None  # garantido no __init__
        return self._settings.openweather_api_key.get_secret_value()

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
