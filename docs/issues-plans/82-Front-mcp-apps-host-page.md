---
issue: 82
title: "[Front] -MCP-APPS- Minimal host page with iframe + AppBridge over postMessage"
branch: feat/mcp-apps-fundamentals-81-83-host-app
status: closed
last_updated: 08-18-2026
---

# Issue #82 — Minimal host page with iframe + AppBridge over postMessage

## Objective
Página de demo isolada (sem CopilotKit/chat) atuando como host MCP Apps: carrega o widget da issue #81 num iframe sandboxed e o dirige via um `AppBridge` sobre `postMessage`, espelhando o exemplo host em vanilla JS do artigo original.

## Scope
- `pages/mcp-apps-host/mcp-apps-host.component.ts` (novo): `McpAppsHostComponent`
- `pages/mcp-apps-host/mcp-apps-host.component.html`/`.scss`
- `app.routes.ts`: rota `/mcp-apps-host` (`loadComponent`)
- `package.json`: dependência `@modelcontextprotocol/ext-apps`
- Reference: `docs/tutorial_A2UI/07-mcp-apps-fundamentals.md` (Passo 2)

## Decisões de implementação
- **`iframe.src` aponta pra rota backend `/mcp-apps/weather-card`** (issue #83, servida por `app/api/routes/mcp_apps.py`), não pro recurso MCP puro — a comunicação MCP protocolar (issue #81) é uma coisa; o iframe precisa de uma URL HTTP direta carregável pelo browser, que é o que essa rota HTML oferece.
- **`AppBridge` inicializado no evento `iframe.onload`**, não no `ngAfterViewInit` direto — o widget dentro do iframe precisa estar carregado e ter registrado seus próprios listeners antes do host tentar `connect()`.
- **`onsizechange` redimensiona o iframe dinamicamente** (`iframe.style.height`), evitando scrollbar — o host não assume uma altura fixa, deixa o widget dizer do que precisa.
- **Import de `@modelcontextprotocol/ext-apps/app-bridge` fica isolado no chunk lazy da rota `/mcp-apps-host`** (via `loadComponent`), confirmado no build: a dependência não aparece no bundle inicial, só é buscada quando a rota é visitada.

## Status
> Atualizado em: 08-18-2026

- [x] `McpAppsHostComponent` implementado: cria o iframe, inicializa `AppBridge`, manda `sendToolInput`/`sendToolResult` mockados, trata `onsizechange`.
- [x] Rota `/mcp-apps-host` registrada, lazy-loaded.
- [x] **Validação funcional:** `ng build` limpo (bundle inicial 1.56 MB, dependência `ext-apps` confirmada fora do chunk inicial). `ng test`: 47/50 — 3 falhas pré-existentes, sem relação.

## Notes
- Implementado originalmente por sessão do Cursor (não commitado); esta issue documenta a versão reorganizada em branch própria, encadeada sobre a Parte 6 (issues #78-80).
