---
issue: 83
title: "[Front] -MCP-APPS- Minimal app page rendering the weather widget from tool input/result"
branch: feat/mcp-apps-fundamentals-81-83-host-app
status: closed
last_updated: 08-18-2026
---

# Issue #83 — Minimal app page rendering the weather widget from tool input/result

## Objective
Lado "app" do par host↔app de MCP Apps: o HTML/JS do widget (`weather_card.html`, issue #81) que recebe input/resultado da tool via `App`/`postMessage`, mandado pelo host construído na issue #82.

## Scope
- `app/mcp/assets/weather_card.html` (issue #81): widget vanilla HTML/CSS/JS, sem framework — mesma abordagem do artigo original, pra manter a mecânica host↔app isolada de qualquer framework
- `app/api/routes/mcp_apps.py` (novo, backend): `GET /api/mcp-apps/weather-card` — serve o HTML diretamente, pra ser carregado no `src` do iframe do host (issue #82)
- Reference: `docs/tutorial_A2UI/07-mcp-apps-fundamentals.md` (Passo 3)

## Decisões de implementação
- **O widget é um arquivo estático servido pelo backend, não um componente Angular.** Diferente do resto do projeto (majoritariamente Angular), o lado "app" de MCP Apps roda **dentro de um iframe isolado** — não faz sentido (e o protocolo não pede) que seja parte da árvore de componentes Angular do host. Isso também mantém a demo fiel ao artigo original (host e app em vanilla JS, sem framework).
- **Uma única rota HTTP (`/api/mcp-apps/weather-card`) serve o mesmo HTML tanto pro caminho MCP puro (via `read_resource`, issue #81) quanto pro caminho de demo direta no browser (`iframe.src`, issue #82).** Evita duplicar o arquivo do widget — `app/mcp/resources.py`/`app/api/routes/mcp_apps.py` leem o mesmo `weather_card.html` por dois caminhos de acesso diferentes (protocolo MCP vs. HTTP direto).

## Status
> Atualizado em: 08-18-2026

- [x] `weather_card.html` implementado: registra `App`, escuta `ontoolinput`/`ontoolresult`, renderiza o card de clima recebido.
- [x] Rota `GET /api/mcp-apps/weather-card` registrada e testada.
- [x] **Validação funcional:** `pytest` (backend) — 129/129, incluindo a leitura do widget via `read_weather_app_resource()` (issue #81). Validação end-to-end (host #82 + app #83) planejada via browser: abrir `/mcp-apps-host`, confirmar que o card de clima mockado renderiza dentro do iframe.

## Notes
- Implementado originalmente por sessão do Cursor (não commitado); esta issue documenta a versão reorganizada em branch própria.
- Fecha a Parte 7 do tutorial (issues #81-83) — próxima: Parte 8 (MCP Apps no Angular com CopilotKit, issues #84-87), que depende desta parte.
