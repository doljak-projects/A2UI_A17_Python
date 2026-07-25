---
issue: 4
title: "BE: Registrar e configurar chave da OpenWeatherMap"
branch: feat/4-openweather-configure-api-key-and-http-client
status: closed
last_updated: 07-25-2026
---

# Issue #4 — BE: Registrar e configurar chave da OpenWeatherMap

## Status
Feita — chave, base URL e cliente HTTP autenticado configurados e testados.

## O que foi feito
- `Settings` (`app/core/config.py`): adicionados `openweather_api_key` (`SecretStr`, opcional) e `openweather_base_url` (default `https://api.openweathermap.org/data/2.5`), mais a propriedade `openweather_configured`.
- `.env.example`: novas variáveis `OPENWEATHER_API_KEY` e `OPENWEATHER_BASE_URL`, com link de registro e aviso de não commitar a chave real.
- `app/services/weather_client.py`: `WeatherClient` (httpx) autenticado via `appid`, com `get_current_weather(city, units, lang)` retornando JSON e suporte a context manager.
- Erros de domínio dedicados: `OpenWeatherError`, `MissingOpenWeatherApiKeyError` (chave ausente) e `CityNotFoundError` (404); 401 e demais status viram `OpenWeatherError` com mensagem clara.
- `httpx` promovido para `requirements.txt` (dependência de runtime).
- Testes em `tests/test_weather_client.py` usando `httpx.MockTransport`: sucesso com verificação dos query params, chave ausente, cidade inexistente, chave inválida, erro de transporte e leitura das settings.

## Como rastrear
- Branch: `feat/4-openweather-configure-api-key-and-http-client`
- Worktree: `4-worktree-openweather`
- Arquivos principais: `apps/backend/app/core/config.py`, `apps/backend/app/services/weather_client.py`, `apps/backend/.env.example`, `apps/backend/tests/test_weather_client.py`

## Notes
- Decisão de design: a chave da OpenWeatherMap é **opcional** no `Settings` (diferente da `llm_api_key`, que é obrigatória). Sem a chave, a aplicação sobe normalmente e apenas o `WeatherClient` falha na instanciação com `MissingOpenWeatherApiKeyError`. Isso evita que uma integração acessória bloqueie o boot do backend.
- Critério de conclusão atendido: cliente instanciado e autenticado, retornando JSON válido — validado com `MockTransport`, sem consumir cota da API real. Para validar contra a API real, basta definir `OPENWEATHER_API_KEY` no `.env` e chamar `WeatherClient().get_current_weather("São Paulo")`.
- Conflito previsto: a issue #2 também adiciona `httpx` ao `requirements.txt`. Se as duas branches forem mergeadas, resolver mantendo uma única linha.
- Commit/push/PR permanecem manuais.
