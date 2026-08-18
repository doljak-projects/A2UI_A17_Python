---
issue: 86
title: "[Front] -MCP-APPS- provideMCPApps() config in app.config.ts"
branch: feat/mcp-apps-copilotkit-84-87-real-chat
status: closed
last_updated: 08-18-2026
---

# Issue #86 — provideMCPApps() config in app.config.ts

## Objective
Registra o renderer de MCP Apps do CopilotKit (`provideMCPApps`), configurando identidade do host e contexto de apresentação — seguindo o mesmo padrão de registro de provider já usado pra CopilotKit (issue #46) e A2UI (issue #52).

## Scope
- `pages/copilot-weather-chat/copilot-weather-chat.routes.ts` (novo)
- `app.routes.ts`: rota `/copilot-weather-chat` trocada de `loadComponent` pra `loadChildren`
- Reference: `docs/tutorial_A2UI/08-mcp-apps-angular-copilotkit.md` (Passo 3)

## Decisões de implementação — desvio proposital do plano original
O plano original desta issue (e o artigo de referência) registra `provideMCPApps(...)` em `app.config.ts`, ao lado dos outros providers globais. **Isso não foi feito aqui.** Ao validar o build, o orçamento de bundle inicial (`angular.json`, ajustado pra 1.6 MB na issue #73) estourava de novo — `provideMCPApps` sozinho adicionava ~260 KB ao bundle inicial, porque `app.config.ts` é importado de forma eager por `main.ts`/`bootstrapApplication`, então qualquer import estático ali (mesmo de um provider só usado numa rota) entra no chunk principal.

Solução aplicada — **lazy-loading do provider, não do build**: criado `copilot-weather-chat.routes.ts`, um arquivo de rotas dedicado (`loadChildren` em vez de `loadComponent` direto), com `providers: [provideMCPApps(...)]` declarado ali dentro. Como esse arquivo só é buscado quando a rota `/copilot-weather-chat` é navegada, o import de `provideMCPApps` (e a dependência `@modelcontextprotocol/ext-apps` que ele carrega) fica isolado no chunk lazy dessa rota — confirmado no build: bundle inicial voltou a 1.56 MB (dentro do teto de 1.6 MB), e o `@modelcontextprotocol/ext-apps` não aparece mais nos chunks iniciais.

- **`hostInfo`/`hostContext` mantidos como no plano original** (`{ name: 'A2UI Weather Chat', version: '1.0.0' }` / tema claro, plataforma web, modo inline) — só o *onde* registrar mudou, não a config em si.
- **`app.config.ts` não foi tocado nesta issue** — `provideCopilotKit`, `provideA2Ui`, `provideMarkdownRenderer` continuam lá; só `provideMCPApps` saiu do escopo global.

## Status
> Atualizado em: 08-18-2026

- [x] `provideMCPApps()` registrado via `copilot-weather-chat.routes.ts` (providers de rota), não em `app.config.ts`.
- [x] **Validação funcional:** `ng build` — bundle inicial 1.56 MB, dentro do orçamento de 1.6 MB; confirmado que `@modelcontextprotocol/ext-apps` só aparece nos chunks lazy (`copilot-weather-chat-routes`), não no inicial. `ng test`: 48/51 — 3 falhas pré-existentes, sem relação.

## Notes
- Implementado originalmente por sessão do Cursor **com `provideMCPApps` em `app.config.ts`** (não commitado) — isso quebrava o orçamento de bundle sozinho. A mudança pra `loadChildren`/providers de rota é uma correção aplicada durante a reorganização desta issue, não parte da implementação original do Cursor.
- Pendência registrada: se o projeto crescer mais rotas que precisem de MCP Apps, vale considerar extrair esse padrão de "rota com providers pesados isolados" pra um helper reutilizável.
