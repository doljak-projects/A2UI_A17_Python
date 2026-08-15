---
issue: 48
title: "[Front] -A2UI- Weather frontend tool via createFrontendTool"
branch: feat/frontend-weather-tool-48-createfrontendtool
status: closed
last_updated: 08-15-2026
---

# Issue #48 — Weather frontend tool via createFrontendTool

## Objective
Reimplement the client-side weather tool (issues #35–#36) using CopilotKit's frontend-tool mechanism, so the tool call is resolved automatically inside a single `runAgent()` call — no manual `AgentSubscriber` capture + second run (issue #36's approach).

## Scope
- Define a `show_weather` frontend tool whose `handler` returns a mocked weather result, reusing the field names from issue #35 (`weatherSchema`/`WeatherToolResult`)
- Register it via `registerFrontendTool`, associated to the `weather-agent` (issue #47)
- Confirm CopilotKit auto-resolves the tool call in a single `runAgent()` call
- Reference: `docs/tutorial_A2UI/02-ag-ui-copilotkit-angular.md` (Passo 4)

## Decisões de arquitetura
- **Sem `createFrontendTool`**: o `.d.ts` de `@copilotkit/angular@0.3.1` não exporta esse helper (citado no tutorial/issue, mas ausente nessa versão do SDK). O que existe é a interface `FrontendToolConfig` (`{ name, description, parameters, handler, agentId? }`), montada como objeto literal e registrada via `registerFrontendTool(...)`. `parameters` aceita um `StandardSchemaV1` — schemas Zod (v3.24+/v4) já implementam esse contrato nativamente, então nenhum `z.toJSONSchema(...)` é necessário aqui (diferente do `Tool` cru do AG-UI usado em `weather-tool-for-a2ui.ts`).
- **Dois schemas, não um**: `weatherToolArgsSchema` (`{ city: string }`, novo, em `weather-frontend-tool.ts`) descreve os *argumentos* que a tool recebe do servidor (`WeatherResumableToolCallAgent`, issue #45 — confirmado em `apps/backend/app/agui/agent.py`: `ToolCallArgsEvent` emite só `{"city": ...}`). Isso é diferente do `weatherSchema` de `weather-tool-for-a2ui.ts` (issue #35), que descreve o *resultado* completo (`city`/`temperature_c`/`description`/`humidity`) devolvido pela tool — os dois papéis não podem compartilhar um schema só.
- **Reaproveitamento real, não duplicação**: `weather-frontend-tool.ts` reexporta `buildMockWeatherResult` de `weather-tool-for-a2ui.ts` (issue #36) em vez de reescrever a lógica do mock.
- **Registro dentro de `initAgentStore()`**: `registerFrontendTool` roda no mesmo ponto de injeção que já registra o agente (issue #47), reaproveitando a mesma guarda de idempotência (`copilotKit.getAgent(...)`) — a tool só é registrada quando o agente ainda não existe.

## Status
> Atualizado em: 2026-08-15

- [x] `apps/frontend/src/app/core/services/weather-frontend-tool.ts` criado: `weatherToolArgsSchema` (`{ city: string }`) + reexport de `buildMockWeatherResult`.
- [x] `weather-agent-store.ts` (issue #47) estendido: `initAgentStore()` agora também chama `registerFrontendTool({ name: 'show_weather', parameters: weatherToolArgsSchema, agentId: 'weather-agent', handler: async ({ city }) => buildMockWeatherResult(city) })`.
- [x] `ng build` limpo (mesmos warnings pré-existentes de budget/CommonJS).
- [x] Spec `weather-frontend-tool.spec.ts` criado — 2 casos: tool registrada e recuperável via `copilotKit.core.getTool({ toolName: 'show_weather', agentId: 'weather-agent' })`, e o `handler` resolvendo pro mock esperado a partir de `{ city }`. `ng test` completo: 41/44 verdes, mesmas 3 falhas pré-existentes de `agui-test.component.spec.ts`, sem regressão nova.

## Notes
- Nenhuma UI dispara `runAgent()` de verdade ainda — validar o ciclo de resolução automática ponta a ponta (uma única run, sem captura manual) fica pra quando a issue #50 (sidecar chat) ligar tudo. Este spec valida o `handler` isoladamente, que é a peça nova desta issue.
- Issue #49 (widget de clima) é o próximo consumidor natural: precisa de um `component: Type<ToolRenderer<WeatherToolResult>>` anexado a esta mesma config de tool.
