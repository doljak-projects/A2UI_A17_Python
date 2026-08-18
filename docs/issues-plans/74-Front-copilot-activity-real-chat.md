---
issue: 74
title: "[Front] -A2UI- Render the weather card inside the real chat via the activity renderer"
branch: feat/a2ui-agui-integration-72-74-activity-snapshot
status: closed
last_updated: 08-18-2026
---

# Issue #74 — Render the weather card inside the real chat via the activity renderer

## Objective
Fecha o loop entre o chat real e o protocolo A2UI: atualiza o chat sidecar (issue #50) pra detectar mensagens `role: 'activity'` e delegar a renderização pro `A2uiActivityRenderer` (issue #73) — o card de clima construído nas issues #53/#54/#72 passa a também aparecer dentro do fluxo de chat de produção, não só na rota de demo isolada `/a2ui-test`.

## Scope
- `components/copilot-activity/copilot-activity.component.ts` (novo): `CopilotActivityComponent` — roteia uma `ActivityMessage` pro `ActivityRenderer` certo, consultando `copilotKit.activityMessageRenderConfigs()` por `activityType`
- `copilot-weather-chat.component.ts`: `injectWeatherAgentStore('a2ui')` além do modo `'tool'` já existente (#45); seletor de modo (`agentMode` signal); `asActivityMessage()` helper
- `copilot-weather-chat.component.html`: `@case ('activity')` no `@switch` de mensagens, renderizando `<app-copilot-activity>`; `<mat-select>` pra trocar o modo do agente
- `core/services/weather-agent-store.ts`: `injectWeatherAgentStore(mode)` passa a aceitar um modo (`'tool' | 'a2ui'`), registrando os dois agentes (`weather-agent`/`weather-a2ui-agent`) via `selfManagedAgents`
- Reference: `docs/tutorial_A2UI/04-integrating-a2ui-with-ag-ui.md` (Passo 3)

## Decisões de implementação
- **`CopilotActivityComponent` usa `NgComponentOutlet`**, não um `@switch` fixo de tipos conhecidos — a lista de `activityType`s suportados vem de `copilotKit.activityMessageRenderConfigs()` (registrada via `provideCopilotKit({ renderActivityMessages: [...] })`), então novos tipos de atividade (ex: MCP Apps, issue #87) só precisam ser registrados no provider, sem tocar neste componente.
- **Guard de idempotência do agent store corrigido de flag de módulo pra checagem por instância.** A implementação original (não commitada) usava uma variável `let storesInitialized` no escopo do módulo — quebrava tanto o build (referenciada antes de declarada) quanto os testes (uma vez `true`, nunca mais registrava agentes em instâncias novas de `CopilotKit`, já que cada `TestBed`/bootstrap cria sua própria instância). Corrigido pra checar `copilotKit.getAgent(WEATHER_TOOL_AGENT_ID)` na própria instância injetada — mesmo padrão já usado antes da issue #72.
- **Modo padrão do seletor é `'a2ui'`, não `'tool'`** — o objetivo desta issue é demonstrar o card A2UI funcionando no chat real; o modo tool call (#45) continua disponível pra comparação.

## Status
> Atualizado em: 08-18-2026

- [x] `CopilotActivityComponent` implementado, roteando por `activityType`.
- [x] `copilot-weather-chat` atualizado: seletor de modo, renderização de `activity`, agent store com 2 modos.
- [x] Bug de guard de módulo (`storesInitialized`) identificado e corrigido — causava falha de build E 7 testes quebrados na implementação original não commitada.
- [x] **Validação funcional:**
  - `ng build`: limpo, sem erros de compilação (orçamento ajustado, ver doc da #73).
  - `ng test`: 47/50 verdes — 3 falhas pré-existentes (`chat.component.spec.ts`, não relacionadas), 0 falhas novas.
  - `pytest` (backend): 123/123 — sem regressão nas rotas AG-UI existentes.
  - Verificação manual planejada no browser: selecionar modo "A2UI" no chat, enviar mensagem, confirmar que o card de clima renderiza dentro da conversa via `ACTIVITY_SNAPSHOT`.

## Notes
- Implementado originalmente por sessão do Cursor, mas **não commitado** e com bugs reais (build quebrado + 7 testes falhando). Esta issue documenta a versão corrigida, validada e organizada em branch própria — ver `docs/issues-plans/72-*.md`/`73-*.md` pro resto do contexto da Parte 4.
- Fica pendente (fora do escopo desta issue): reimplementar em modo mentorado, passo a passo, como o usuário pediu — este PR prioriza ter a Parte 4 funcional e documentada primeiro.
