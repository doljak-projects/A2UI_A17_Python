---
issue: 5
title: "BE: Criar tool get_weather(city) consumindo a OpenWeatherMap"
branch: feat/5-weather-tool-create-get-weather-tool
status: closed
last_updated: 07-25-2026
---

# Issue #5 — Tool `get_weather(city)` chamável pelo LLM

## Status
Feita — serviço, schema de saída, tool registrada e testes; validada contra a API real.

## O que foi feito
- `app/schemas/weather.py`: modelo `WeatherResult` com `city`, `temperature_c`, `description` e `humidity`, cada campo descrito para o LLM.
- `app/services/weather.py`: função `get_weather(city, client=None)` que consulta o `WeatherClient` e normaliza o payload da WeatherAPI (`location`/`current`) em `WeatherResult`. Sem `client`, a função cria e fecha o seu próprio cliente; payload malformado vira `WeatherApiError`.
- `app/tools/weather.py`: `GetWeatherTool` (nome `get_weather`, JSON Schema com o argumento obrigatório `city`) e `register_weather_tools()` idempotente.
- `app/tools/__init__.py`: passa a registrar as tools de clima junto com as embutidas ao importar o pacote.
- `tests/test_weather_tool.py`: 8 testes cobrindo normalização do payload, criação do cliente próprio, cidade inexistente, payload malformado, formato do schema, registro no registry padrão e execução via `execute_tool`.

## Como rastrear
- Branch: `feat/5-weather-tool-create-get-weather-tool`
- Worktree: `5-worktree-weather-tool`
- Arquivos principais: `apps/backend/app/services/weather.py`, `apps/backend/app/schemas/weather.py`, `apps/backend/app/tools/weather.py`, `apps/backend/tests/test_weather_tool.py`

## Notes
- A issue foi escrita para a OpenWeatherMap, mas o provedor foi migrado para a WeatherAPI.com na #14; a tool consome o cliente já migrado.
- O `WeatherClient` é instanciado **dentro** de `execute()`, não no construtor da tool: assim o registro no boot não quebra quando a `WEATHER_API_KEY` não está configurada — a falta da chave só aparece como erro na execução.
- `city` no resultado é a localidade **resolvida** pela WeatherAPI, não a string enviada. Com `lang=pt`, "São Paulo" volta como "San Paulo"; é o dado da API, não uma normalização nossa.
- A WeatherAPI faz fuzzy match generoso: "Narnia" resolve para a cidade italiana de mesmo nome. O `CityNotFoundError` (código 1006) só dispara com entradas realmente sem correspondência.
- Validação: 27 testes passando + chamadas reais retornando `Lisboa 25.3 C / 61%` e `CityNotFoundError` no caminho de erro.
- A tool já fica disponível no `registry`, então o loop de tool calling da #2 (PR #16) a enxerga automaticamente assim que as duas branches estiverem na `main`.
