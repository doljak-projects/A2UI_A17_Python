---
issue: 36
title: "[Front] -A2UI- Two-run cycle for client-side weather tool call result"
branch: feat/weather-tool-two-run-36-client-side-cycle
status: ready-for-review
last_updated: 2026-08-01
---

# Issue #36 — Two-run cycle for client-side weather tool call result

## Objective
Implement the full client-side tool call cycle: a first run with `tools: [showWeatherTool]`, inspect the response for a client-side tool call request, execute the corresponding local action, build the tool call result message, add it via `agent.addMessage(...)`, and trigger a second run. This closes the server-side vs. client-side tool call cycle described in the tutorial, within the A2UI chat flow.

## Scope
- Trigger 1st `runAgent` call with `tools: [showWeatherTool]`
- Detect client-side tool call requests from the received events
- Execute the corresponding client action and build the tool call result message
- Add the result message via `agent.addMessage(...)`
- Trigger the 2nd `runAgent` call to resume the conversation
- Reference: `docs/tutorial_A2UI/01-ag-ui-sdk-typescript.md` (Passo 5)

## Modo de trabalho desta issue
Mesmo formato mentorado das issues #34/#35: conceito explicado antes do código, confirmação do usuário, só então o código — passos pequenos. Decisões registradas neste doc.

## Decisão de arquitetura (antes do Passo 1)
Os dois endpoints de demo existentes (`/agui/demo`, `/agui/weather-tool-demo`) resolvem a tool call **inteiramente no servidor** — nenhum deixa uma tool call pendente pro cliente. Para esta issue fazer sentido (ciclo **client-side**), é necessário um novo agente/endpoint de demo no backend que emita `TOOL_CALL_START/ARGS/END` sem resolver, terminando em `RUN_FINISHED` — deixando a tool call em aberto para o `AgentSubscriber` detectar e o cliente executar.

Decisão do usuário sobre a "execução client-side": o servidor manda os `args` da tool call (ex: `{"city": "São Paulo"}`), e o cliente "executa" localmente construindo um resultado de clima a partir desses args (não busca clima real — não há API key no browser). Motivo: preparar o terreno para os args crescerem em complexidade em etapas futuras, em vez de o cliente decidir tudo sozinho sem nada vindo do servidor.

**Limitação descoberta durante o Passo 1:** como a `AguiGetHttpAgent` (#34) sobrescreve `requestInit()` para `GET` sem corpo, o `agent.addMessage(toolResultMessage)` feito pelo cliente antes da 2ª run **nunca chega ao backend** — a rota sempre monta um `RunAgentInput` novo com `messages=[]`. Ou seja, o backend não reage de fato ao resultado da tool call nesse transporte. Decisão do usuário: a 2ª run aponta para `GET /api/agui/demo` (`WeatherChatAgent`, só texto) para demonstrar visualmente que uma segunda chamada acontece e a conversa "retoma" — sem fingir que o backend viu o resultado, já que essa é uma limitação conhecida do transporte GET-only, fora do escopo desta issue resolver (exigiria voltar a `POST` com corpo na #34).

## Status
> Atualizado em: 2026-08-01

- [x] Passo 1 — Backend: `WeatherClientToolCallAgent` (`app/agui/agent.py`) + rota `GET /api/agui/weather-tool-client-demo`, emitindo `TOOL_CALL_START` (`show_weather`) → `TOOL_CALL_ARGS` (`{"city": "São Paulo"}`) → `TOOL_CALL_END` → `RUN_FINISHED`, sem `TOOL_CALL_RESULT`. Validado via `curl` — sequência exata esperada.
- [x] Passo 2 — `createWeatherToolCallCapture()` adicionado em `weather-tool-for-a2ui.ts`: monta um `AgentSubscriber` de uma run só (2º parâmetro de `runAgent(params, subscriber)`, sem mexer no `aguiLogSubscriber` permanente) com `onToolCallEndEvent`, que já entrega `toolCallArgs` parseado pelo SDK — filtra por `toolCallName === 'show_weather'` e resolve uma `Promise<{ toolCallId, city }>`.
- [x] Passo 3 — `buildMockWeatherResult(city)` adicionado em `weather-tool-for-a2ui.ts`: monta um `WeatherToolResult` com dados fixos (22°C, "Parcialmente nublado", 60% umidade) para a cidade recebida — sem chamada de API real, não há chave de clima no browser.
- [x] Passo 4 — `AguiTestComponent.runAgent()` monta a `ToolMessage` (`role: 'tool'`, `toolCallId` capturado no Passo 2, `content` = `buildMockWeatherResult` serializado) e chama `agent.addMessage(...)`.
- [x] Passo 5 — Adicionado `AguiAgentService.pointAt(path)` (muda a `url` da instância compartilhada de `AguiGetHttpAgent` — só a URL importa, já que `requestInit()` ignora o corpo). `AguiTestComponent` aponta para `/agui/weather-tool-client-demo` na 1ª run e `/agui/demo` na 2ª, disparando `agent.runAgent()` de novo para retomar.
- [x] Passo 6 — Testes: backend `test_agui_weather_client_tool_agent.py` (5 casos) + `test_agui_weather_client_tool_endpoint.py` (2 casos), 111/111 na suíte completa do backend, `ruff check` limpo. Frontend: `weather-tool-for-a2ui.spec.ts` (+3 casos), `agui-agent.service.spec.ts` (+1, `pointAt`), `agui-test.component.spec.ts` (reescrito pro ciclo de duas runs) — 17/17 verdes nos arquivos da issue; suíte completa 36/39 (as mesmas 3 falhas pré-existentes de `chat.component.spec.ts`). Validação manual: usuário faz por conta própria.

## Notes
- `ChatService`/`ChatComponent` existentes **não são tocados** nesta issue.
- O agente novo do backend é só uma demo didática (como `WeatherChatAgent`/`WeatherToolCallAgent` das #32/#33) — não substitui nem altera os agentes existentes.
