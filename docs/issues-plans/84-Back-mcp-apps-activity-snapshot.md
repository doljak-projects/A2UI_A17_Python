---
issue: 84
title: "[Back] -MCP-APPS- Emit an ACTIVITY_SNAPSHOT (mcp-apps) with the weather MCP App's tool result"
branch: feat/mcp-apps-copilotkit-84-87-real-chat
status: closed
last_updated: 08-18-2026
---

# Issue #84 — Emit an ACTIVITY_SNAPSHOT (mcp-apps) with the weather MCP App's tool result

## Objective
Empacota a metadata do widget MCP Apps de clima (issue #81) e o resultado estruturado de `get_weather` num evento AG-UI `ACTIVITY_SNAPSHOT`, reutilizando o mesmo mecanismo de transporte já implementado pra A2UI (issue #72), agora com `activityType: 'mcp-apps'`.

## Scope
- `app/agui/agent.py`: nova classe `WeatherMcpAppsActivityAgent`
- `app/agui/a2ui_constants.py`: `MCP_APPS_ACTIVITY_TYPE`, `WEATHER_MCP_SERVER_HASH`
- `app/api/routes/agui.py`: nova rota `POST /api/agui/weather-mcp-apps-agent-demo`
- Reference: `docs/tutorial_A2UI/08-mcp-apps-angular-copilotkit.md` (Passo 1)

## Decisões de implementação
- **Reaproveita o `ACTIVITY_SNAPSHOT`, não um evento AG-UI novo.** O mecanismo de transporte é idêntico ao da issue #72 (A2UI); só o `activityType` e o `content` mudam. Isso significa que o roteamento de atividades no frontend (`CopilotActivityComponent`, issue #74) já funciona pro MCP Apps sem alteração — só precisa de um renderer registrado pro tipo `'mcp-apps'` (issue #86).
- **`content` carrega `resourceUri` + `toolInput` + `result` (com `content`/`structuredContent`)** — o mesmo formato que `sendToolResult()` usaria no protocolo MCP Apps puro (issue #82), só que entregue via AG-UI em vez de `postMessage` direto.
- **Depende da Parte 7 (issues #81-83)** — reaproveita `WEATHER_MCP_RESOURCE_URI` e a mecânica de resource já implementada lá.

## Status
> Atualizado em: 08-18-2026

- [x] `WeatherMcpAppsActivityAgent` implementado, rota registrada.
- [x] **Validação funcional:** `pytest` — `test_weather_mcp_apps_agent_emits_mcp_apps_snapshot` confirma a sequência `RUN_STARTED`/`ACTIVITY_SNAPSHOT`/`RUN_FINISHED`, `activityType: 'mcp-apps'`, e `resourceUri`/`structuredContent` corretos. 133/133 no total do backend.

## Notes
- Implementado originalmente por sessão do Cursor (não commitado); esta issue documenta a versão reorganizada em branch própria, encadeada sobre a Parte 7 (issues #81-83).
