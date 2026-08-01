---
issue: 33
title: "[Back] -A2UI- Wire existing get_weather tool as an AG-UI server-side tool call"
branch: feat/agui-weather-tool-33-server-side-call
status: closed
last_updated: 07-28-2026
---

# Issue #33 — Wire existing get_weather tool as an AG-UI server-side tool call

## Diagrama
Ver [`docs/diagrams/backend-agui-agent.md`](../diagrams/backend-agui-agent.md) — hierarquia de classes e fluxo requisição → SSE (cobre #32 e #33).

## Objective
Extend the AG-UI agent skeleton from issue #32 so that, within the same `run`, it emits a server-side tool call sequence and resolves it using the project's existing `get_weather(city)` tool (`apps/backend/app/services/weather.py`, issue #5), instead of mocking the result as the original tutorial does.

## Scope
- Emit `TOOL_CALL_START` → `TOOL_CALL_ARGS` → `TOOL_CALL_END` for a weather lookup
- Execute the tool call server-side by invoking the existing `get_weather(city)` service
- Emit `TOOL_CALL_RESULT` with the real weather payload
- Reference: `docs/tutorial_A2UI/01-ag-ui-sdk-typescript.md` (Passo 2)

## Arquitetura

Segue a mesma decisão registrada na issue #32 (ver `docs/issues-plans/32-Back-ag-ui-agent-skeleton.md`): implementação em **Python**, com o pacote `ag-ui-protocol`, reutilizando `AGUIAgent` (a classe base equivalente ao `AbstractAgent` do artigo). Nenhuma tag-Node nova é introduzida.

Diferente do `WeatherChatAgent` (#32), que só emite texto, o `WeatherToolCallAgent` (#33) reproduz o passo "Tool Call no Servidor" do artigo:

1. `TOOL_CALL_START` (`tool_call_id`, `tool_call_name="get_weather"`)
2. `TOOL_CALL_ARGS` (`delta` com o JSON dos argumentos, ex.: `{"city": "São Paulo"}`)
3. `TOOL_CALL_END`
4. Execução real: chama `get_weather(city)` (issue #5), **sem mock** — diferente do artigo, que hardcoda o resultado
5. `TOOL_CALL_RESULT` (`content` com o JSON do `WeatherResult` real)

A cidade é fixa (`"São Paulo"`), no mesmo espírito didático do `WeatherChatAgent` — não há LLM decidindo dinamicamente o argumento nesta issue.

## Status
> Atualizado em: 07-28-2026

- [x] Nova classe `WeatherToolCallAgent(AGUIAgent)` em `app/agui/agent.py`, emitindo `TOOL_CALL_START/ARGS/END` e `TOOL_CALL_RESULT`
- [x] Execução real do `get_weather("São Paulo")` (sem mock) dentro do `run()`
- [x] Testes cobrindo a sequência de eventos e o payload real — `tests/test_agui_weather_tool_agent.py` (7 testes)
- [x] Rota HTTP de demo — `GET /api/agui/weather-tool-demo` (`app/api/routes/agui.py`), com `tests/test_agui_weather_tool_endpoint.py` (3 testes)
- [x] Tratamento de erro na rota: falha do `get_weather` (ex.: chave inválida, cidade não encontrada) agora vira um evento `RunErrorEvent` (`RUN_ERROR`) em vez de simplesmente cortar o stream — mesma estratégia que `/api/chat` já usa, adaptada ao AG-UI
- Suíte completa do backend: **104 passed**, `ruff check` limpo

## Como testar funcionalmente

### Backend

```bash
cd apps/backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Em outro terminal, com `WEATHER_API_KEY` válida configurada no `.env` (veja `.env.example`):

```bash
curl -N http://127.0.0.1:8000/api/agui/weather-tool-demo
```

Saída esperada, com clima real de São Paulo:

```
data: {"type":"RUN_STARTED","threadId":"<uuid>","runId":"<uuid>"}

data: {"type":"TOOL_CALL_START","toolCallId":"2001","toolCallName":"get_weather"}

data: {"type":"TOOL_CALL_ARGS","toolCallId":"2001","delta":"{\"city\": \"São Paulo\"}"}

data: {"type":"TOOL_CALL_END","toolCallId":"2001"}

data: {"type":"TOOL_CALL_RESULT","messageId":"3001","toolCallId":"2001","content":"{\"city\":\"...\",\"temperature_c\":...,\"description\":\"...\",\"humidity\":...}","role":"tool"}

data: {"type":"RUN_FINISHED","threadId":"<uuid>","runId":"<uuid>"}
```

**Sem uma `WEATHER_API_KEY` válida** (ex.: placeholder do `.env.example`), a chamada real à WeatherAPI falha e o stream termina com um evento de erro em vez do `TOOL_CALL_RESULT`:

```
data: {"type":"RUN_ERROR","message":"Chave da WeatherAPI inválida ou não autorizada: API key is invalid."}
```

Isso foi testado manualmente (curl contra o servidor real, sem chave válida) antes de existir o tratamento de erro — o stream simplesmente cortava depois do `TOOL_CALL_END`, sem sinalizar falha ao cliente. O `try/except` + `RunErrorEvent` foi adicionado por causa dessa observação.

Alternativa sem subir servidor, mockando `get_weather` direto em Python:

```python
from unittest import mock
from ag_ui.core import RunAgentInput
from ag_ui.encoder import EventEncoder
from app.schemas.weather import WeatherResult
from app.agui.agent import WeatherToolCallAgent

fake = WeatherResult(city="Sao Paulo", temperature_c=18.1, description="Parcialmente nublado", humidity=77)
with mock.patch("app.agui.agent.get_weather", return_value=fake):
    run_input = RunAgentInput(
        thread_id="t1", run_id="r1",
        state=None, messages=[], tools=[], context=[], forwarded_props={},
    )
    encoder = EventEncoder()
    for event in WeatherToolCallAgent().run(run_input):
        print(encoder.encode(event), end="")
```

### Frontend

Ainda **não há nada no frontend** para esta issue — igual à #32, o consumo do lado cliente é escopo da issue #34 (`[Front] -AG-UI- Consume agent events via HttpAgent and AgentSubscriber`). Quando a #34 existir, o teste funcional de frontend para tool calls server-side passa a ser: no DevTools (Network → EventStream), confirmar que o `AgentSubscriber` recebe e trata os eventos `TOOL_CALL_*` sem quebrar o fluxo — mesmo tipo de verificação já documentada na #32, agora cobrindo também a família de eventos de tool call.

## Notes
- `RunErrorEvent` (`ag_ui.core`) tem `message` e `code` — usamos só `message` por ora, com `str(exc)` da exceção capturada.
- O `content` do `TOOL_CALL_RESULT` usa `result.model_dump_json()` (string JSON), não `model_dump()` (dict) — o schema Pydantic do `ToolCallResultEvent.content` espera uma string.
- Reaproveitar `get_weather` direto (em vez de ir pela `GetWeatherTool`/`ToolRegistry` do LLM tool-calling existente) foi deliberado: o AG-UI é o próprio mecanismo de tool calling aqui, então a camada `ToolRegistry` (usada pelo `/api/chat` para o tool-calling do LLM) não se aplica — ela existe para o LLM decidir *qual* tool chamar; aqui a chamada já está fixa no agente, só a execução é real.
