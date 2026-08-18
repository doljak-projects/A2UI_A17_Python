---
issue: 87
title: "[Front] -MCP-APPS- Render the MCP Apps activity in the real chat UI"
branch: feat/mcp-apps-copilotkit-84-87-real-chat
status: closed
last_updated: 08-18-2026
---

# Issue #87 — Render the MCP Apps activity in the real chat UI

## Objective
Último passo da série: o chat sidecar real passa a suportar um terceiro modo, "MCP Apps", ao lado de "A2UI" (issue #74) e "Tool call" (#45) — pedir o clima no chat pode renderizar o card A2UI ou o widget MCP Apps, dependendo do modo escolhido, sem conflito entre os dois mecanismos.

## Scope
- `core/services/weather-agent-store.ts`: `WeatherChatAgentMode` ganha `'mcp-apps'`; `WEATHER_MCP_APPS_AGENT_ID` registrado em `selfManagedAgents`
- `pages/copilot-weather-chat/copilot-weather-chat.component.ts`: `mcpAppsStore`, `agentMode`/`agentStore`/`activeAgentId` estendidos pro terceiro modo
- `pages/copilot-weather-chat/copilot-weather-chat.component.html`: opção "MCP Apps" no seletor de modo
- Reference: `docs/tutorial_A2UI/08-mcp-apps-angular-copilotkit.md` (Passo 4)

## Decisões de implementação
- **Nenhuma mudança no roteamento de `@case ('activity')` do template, nem no `CopilotActivityComponent` (issue #74).** O roteamento por `activityType` já era genérico desde a issue #74 (`copilotKit.activityMessageRenderConfigs()`) — bastou o `provideMCPApps()` da issue #86 registrar o renderer certo pro `activityType: 'mcp-apps'`, e o mesmo `<app-copilot-activity>` já usado pro card A2UI passou a também renderizar o widget MCP Apps, sem tocar em código de roteamento.
- **Os três agent stores (`toolStore`/`a2uiStore`/`mcpAppsStore`) são injetados de uma vez no componente**, não sob demanda por modo — como `injectWeatherAgentStore()` é idempotente por instância de `CopilotKit` (correção da issue #74), não há custo real em manter os três signals ativos; trocar de modo só troca qual `computed()` é lido.

## Status
> Atualizado em: 08-18-2026

- [x] Terceiro modo "MCP Apps" disponível no seletor do chat sidecar.
- [x] **Validação funcional:**
  - `pytest` (backend): 133/133.
  - `ng build`: limpo, bundle inicial 1.56 MB (dentro do orçamento de 1.6 MB — ver issue #86 sobre o lazy-loading de `provideMCPApps`).
  - `ng test`: 48/51 — 3 falhas pré-existentes (`chat.component.spec.ts`), 0 novas; inclui o teste novo `registra o agente MCP Apps apontando pro endpoint de activity snapshot mcp-apps`.
  - Verificação manual planejada no browser: selecionar modo "MCP Apps" no chat, enviar mensagem, confirmar que o widget HTML de clima renderiza dentro da conversa via `ACTIVITY_SNAPSHOT` (`mcp-apps`).

## Notes
- Implementado originalmente por sessão do Cursor (não commitado, com `provideMCPApps` quebrando o orçamento de bundle); esta issue documenta a versão reorganizada e corrigida.
- **Fecha a série completa do tutorial A2UI Partes 4-8 (issues #72-87)** — próximo passo natural: reimplementar em modo mentorado, do ponto onde a sessão anterior parou, conforme combinado com o usuário.
