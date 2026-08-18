---
issue: 85
title: "[Back] -MCP-APPS- Backend proxy middleware routing widget resource/tool requests"
branch: feat/mcp-apps-copilotkit-84-87-real-chat
status: closed
last_updated: 08-18-2026
---

# Issue #85 — Backend proxy middleware routing widget resource/tool requests

## Objective
O artigo de referência proxeia requisições de recurso/tool do widget através de um middleware Node (`@ag-ui/mcp-apps-middleware`), pra nunca expor o servidor MCP diretamente ao browser. Sem equivalente confirmado em Python, esta issue implementa o mesmo comportamento manualmente: roteando requisições vindas do widget (dentro do chat real) pro servidor MCP interno.

## Scope
- `app/agui/mcp_proxy.py` (novo): `execute_proxied_mcp_request(request)` — trata `resources/read` e `tools/call`, devolvendo o formato que o `AppBridge`/`App` esperariam receber
- `app/agui/agent.py`: `AGUIAgent._proxy_mcp_request_events()` (método na classe base) — checa `forwarded_props.__proxiedMCPRequest` e delega pro proxy
- `WeatherMcpAppsActivityAgent.run()` verifica esse campo antes do fluxo normal
- Reference: `docs/tutorial_A2UI/08-mcp-apps-angular-copilotkit.md` (Passo 2)

## Decisões de implementação
- **O proxy não é uma rota HTTP separada — vive dentro do próprio agente AG-UI.** Diferente do middleware Node do artigo (que intercepta requisições HTTP antes de chegar ao agente), aqui o CopilotKit encaminha a requisição proxied como parte do `RunAgentInput.forwarded_props`, então o agente já recebe a requisição junto do próprio ciclo de `run()` — não precisou de infraestrutura de middleware adicional no FastAPI.
- **`_proxy_mcp_request_events()` fica na classe base `AGUIAgent`, não só em `WeatherMcpAppsActivityAgent`.** Deixa o mecanismo disponível pra qualquer agente futuro que precise atender requisições proxied, sem duplicar a lógica — mesmo que hoje só o agente de MCP Apps efetivamente receba esse tipo de requisição em produção.
- **`execute_proxied_mcp_request` reaproveita `registry.execute_tool()` (o `ToolRegistry` da issue #6) pra `tools/call`**, em vez de reimplementar a execução de tools — a mesma tool `get_weather` (ou qualquer outra registrada) fica acessível tanto via MCP Server real (issue #7) quanto via este proxy.
- **Erros viram `McpProxyError` → `RunFinishedEvent(result={ isError: True, ... })`**, não uma exceção não tratada — o widget precisa de uma resposta estruturada mesmo em caso de erro, não um stream quebrado.

## Status
> Atualizado em: 08-18-2026

- [x] `execute_proxied_mcp_request` implementado (`resources/read`, `tools/call`).
- [x] `_proxy_mcp_request_events` na classe base, usado por `WeatherMcpAppsActivityAgent`.
- [x] **Validação funcional:** `pytest` — `test_mcp_proxy_reads_weather_resource`, `test_mcp_proxy_calls_a_registered_tool` (usa a tool `echo`, sem dependência de API externa) e `test_agent_routes_proxied_mcp_request_instead_of_normal_flow` (confirma que uma requisição proxied produz `RUN_STARTED`/`RUN_FINISHED` sem `ACTIVITY_SNAPSHOT`, ou seja, não reentra no fluxo normal do agente). 133/133 no total.

## Notes
- Implementado originalmente por sessão do Cursor (não commitado); esta issue documenta a versão reorganizada em branch própria.
