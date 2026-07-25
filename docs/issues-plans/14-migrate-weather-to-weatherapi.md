---
issue: 14
title: "[Backend] Migrate weather integration from OpenWeatherMap to WeatherAPI.com"
branch: refactor/14-weather-provider-migrate-to-weatherapi
status: closed
last_updated: 07-25-2026
---

# Issue #14 — Migrar integração de clima da OpenWeatherMap para a WeatherAPI.com

## Status
Feita — cliente, settings, `.env.example` e testes migrados; validado contra a API real.

## O que foi feito
- `Settings`: `openweather_api_key`/`openweather_base_url` renomeados para `weather_api_key`/`weather_base_url` (default `https://api.weatherapi.com/v1`), e `openweather_configured` virou `weather_configured`.
- `app/services/weather_client.py` reescrito para a WeatherAPI: endpoint `/current.json`, autenticação pelo query param `key` (antes era `appid`) e parâmetros `q`, `lang`, `aqi`.
- Erros renomeados e remapeados por **código da API**, não por status HTTP: `CityNotFoundError` (1006), chave inválida/desabilitada/sem acesso (1002, 2006, 2008, 2009), `WeatherQuotaExceededError` (2007), e `WeatherApiError` para o resto. `MissingOpenWeatherApiKeyError` virou `MissingWeatherApiKeyError`.
- `.env.example`: `OPENWEATHER_*` substituídas por `WEATHER_API_KEY` e `WEATHER_BASE_URL`, com link de registro da WeatherAPI.
- `tests/test_weather_client.py` reescrito para o payload (`location`/`current`) e os códigos de erro da WeatherAPI, com parametrização dos códigos de chave inválida.

## Como rastrear
- Branch: `refactor/14-weather-provider-migrate-to-weatherapi`
- Worktree: `14-worktree-weather-provider`
- Arquivos principais: `apps/backend/app/core/config.py`, `apps/backend/app/services/weather_client.py`, `apps/backend/.env.example`, `apps/backend/tests/test_weather_client.py`

## Notes
- Motivo da migração: a issue #4 foi implementada contra a OpenWeatherMap, mas o projeto usa a WeatherAPI.com. A chave real (31 chars) retornava 401 na OpenWeatherMap porque é de outro serviço — não estava truncada.
- Diferença estrutural importante: a WeatherAPI devolve **HTTP 400 com `error.code` 1006** para cidade inexistente, então o mapeamento precisa olhar o código do corpo, não só o status.
- Validação: 20 testes passando + chamada real retornando `Sao Paulo | 18.1 C | Parcialmente nublado` e `CityNotFoundError` corretamente disparado.
- **Ação necessária após o merge**: renomear no `.env` local `OPENWEATHER_API_KEY` → `WEATHER_API_KEY` e `OPENWEATHER_BASE_URL` → `WEATHER_BASE_URL` (o `.env` não é versionado).
- A issue #5 (`get_weather`) deve ser construída sobre este cliente.
