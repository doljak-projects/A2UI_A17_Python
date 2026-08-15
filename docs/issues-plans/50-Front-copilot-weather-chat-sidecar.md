---
issue: 50
title: "[Front] -A2UI- Sidecar chat UI wired to the CopilotKit agent store"
branch: feat/copilot-weather-chat-50-sidecar
status: closed
last_updated: 2026-08-15
---

# Issue #50 — Sidecar chat UI wired to the CopilotKit agent store

## Objective
Montar uma UI de chat de demonstração isolada (mesmo princípio de isolamento do `/agui-test`), usando `agent.addMessage()` + `copilotKit.core.runAgent({ agent })` e renderizando `messages()`/`isRunning()` do agent store — sem tocar em `ChatComponent`/`ChatService`.

## Scope
- Rota isolada `/copilot-weather-chat`
- Consumir `injectWeatherAgentStore()` (issue #47)
- Renderizar mensagens do usuário e do assistente; tool calls via `<copilot-render-tool-calls>`
- Reference: `docs/tutorial_A2UI/02-ag-ui-copilotkit-angular.md` (Passo 6)

## Status
> Atualizado em: 2026-08-15

- [x] `CopilotWeatherChatComponent` criado em `apps/frontend/src/app/pages/copilot-weather-chat/` — headless chat com Material, `send()` via `addMessage` + `runAgent`, signals `messages()`/`isRunning()`.
- [x] Rota lazy `/copilot-weather-chat` adicionada em `app.routes.ts`.
- [x] Assistant messages com `toolCalls` renderizam `<copilot-render-tool-calls [agentId]="weather-agent">`.
- [x] Spec `copilot-weather-chat.component.spec.ts` — 3 casos (título, envio dispara `runAgent`, input vazio ignorado).

## Notes
- O SDK `@copilotkit/angular@0.3.1` não exporta `sendMessage` — o padrão documentado é `addMessage` + `core.runAgent`.
- O widget customizado da issue #49 é anexado à tool no `weather-agent-store.ts` e aparece automaticamente neste chat via `copilot-render-tool-calls`.
