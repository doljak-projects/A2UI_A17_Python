---
issue: 45
title: "[Back] -AG-UI- Accept a real RunAgentInput via POST for a resumable weather tool-call agent"
branch: feat/weather-tool-post-45-resumable-agent
status: ready-for-review
last_updated: 2026-08-01
---

# Issue #45 — Accept a real RunAgentInput via POST for a resumable weather tool-call agent

## Objective
Extend the AG-UI demo backend so a client-side tool call can actually be resumed across two runs: a new endpoint accepts a real POST body (`RunAgentInput` with `messages`), and — depending on whether a tool result message answering `show_weather` is already present — either emits the pending tool call or replies with a final text confirmation. This resolves the limitation documented in issue #36, where the second run couldn't reach the backend because the demo transport was GET-only without a body.

## Scope
- Add `POST /api/agui/weather-tool-agent-demo` accepting a full `RunAgentInput` body
- Implement a new agent (or extend an existing one) that inspects `input.messages` for a `tool` message answering `show_weather`
- If absent: emit `TOOL_CALL_START` → `TOOL_CALL_ARGS` → `TOOL_CALL_END` (pending) → `RUN_FINISHED`
- If present: emit a `TEXT_MESSAGE_START/CONTENT/END` reply acknowledging the weather data → `RUN_FINISHED`
- Reference: `docs/tutorial_A2UI/02-ag-ui-copilotkit-angular.md` (Passo 1)

## Modo de trabalho desta issue
Mesmo formato mentorado das issues #34/#35/#36: conceito explicado antes do código, confirmação do usuário, só então o código — passos pequenos. Decisões registradas neste doc.

## Status
> Atualizado em: 2026-08-01

- [x] Passo 1 — Rota `POST /api/agui/weather-tool-agent-demo` criada em `app/api/routes/agui.py`, recebendo `run_input: RunAgentInput` direto como corpo (não precisou de schema novo — `RunAgentInput` já é um modelo Pydantic do `ag_ui.core`). `_stream`/`_event_stream` refatorados pra aceitar um `run_input` opcional (as rotas GET continuam montando um vazio internamente; a rota POST passa o real). `WeatherResumableToolCallAgent` criado como esqueleto (`RUN_STARTED` → `RUN_FINISHED`). Validado via `curl -X POST` com corpo JSON real — `thread_id`/`run_id` do cliente ecoados na resposta, confirmando que o corpo chega até o agente.
- [x] Passo 2 — `_find_tool_result(input)` adicionado: percorre `input.messages` (union discriminada por `role`, já parseada em tipos concretos pelo Pydantic) procurando uma `ToolMessage` com `tool_call_id == self.TOOL_CALL_ID`. Backend é stateless entre requisições — essa é a única forma de saber se o cliente já resolveu a tool call.
- [x] Passo 3 — `_request_tool_call()` adicionado, chamado quando `_find_tool_result` devolve `None`. `run()` agora ramifica: sem resultado → tool call pendente; com resultado → `NotImplementedError` (placeholder do Passo 4). Validado via `curl -X POST` com `messages: []` — sequência `RUN_STARTED → TOOL_CALL_START/ARGS/END → RUN_FINISHED` confirmada, sem `TOOL_CALL_RESULT`.
- [x] Passo 4 — `_acknowledge_tool_result(tool_result)` adicionado: parseia o `content` da `ToolMessage` (JSON com `city`/`temperature_c`/`description`/`humidity`) e emite uma resposta de texto confirmando os dados. Validado via `curl` simulando o ciclo completo de duas requisições (1ª sem `messages`, 2ª com a `ToolMessage` de resultado) — a 2ª respondeu com texto real citando os dados enviados, confirmando pela primeira vez que o backend reage de fato ao resultado da tool call (resolve a limitação da #36).
- [x] Passo 5 — Testes: `test_agui_weather_resumable_tool_agent.py` (9 casos — ramos com/sem resultado, ignora `tool_call_id` diferente, ids de run) + `test_agui_weather_resumable_tool_endpoint.py` (5 casos — POST real via `TestClient`, ramos com/sem resultado, corpo malformado → 422). 10/10 verdes nos arquivos da issue; suíte completa do backend 121/121, `ruff check` limpo. Validação manual via `curl` já feita nos Passos 1/3/4 (ciclo completo de duas requisições confirmado).

## Notes
- Este endpoint não substitui `/agui/weather-tool-client-demo` (issue #36) nem `/agui/weather-tool-demo` (issue #33) — ambos continuam existindo como demos didáticas anteriores. Este é um endpoint novo, usado pelas issues de frontend da Parte 2 (#46–#50).
- `AguiGetHttpAgent` (issue #34) não é usada aqui — o consumidor deste endpoint (Parte 2, CopilotKit) usa `HttpAgent` no modo `POST` padrão do SDK, sem o override de GET.
