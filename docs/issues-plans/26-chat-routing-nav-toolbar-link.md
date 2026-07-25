---
issue: 26
title: "FE: Rota /chat e link de navegação na toolbar"
branch: feat/26-chat-routing-nav-toolbar-link
status: closed
last_updated: 07-25-2026
---

# Issue #26 — Rota `/chat` e navegação na toolbar

## Status
Feita — chat acessível em `/chat`, raiz redireciona para lá, links na toolbar com destaque ativo.

## O que foi feito
- `app.routes.ts`: `''` redireciona para `/chat`; rota lazy `chat` carrega `ChatComponent`; `/home` mantém a página de boas-vindas; wildcard volta para `/chat`.
- `app.component.html`: links `routerLink` para Chat e Início na toolbar, com `routerLinkActive` e classe `nav-link-active`.
- `app.component.ts`: importa `RouterLink` e `RouterLinkActive`; remove botão de menu e link externo do Material.
- `app.routes.spec.ts`: 3 testes de redirect e navegação; `app.component.spec.ts` atualizado com stub do `ChatService` e verificação dos links.

## Como rastrear
- Branch: `feat/26-chat-routing-nav-toolbar-link`
- Worktree: `26-worktree-chat-routing`
- Arquivos principais: `apps/frontend/src/app/app.routes.ts`, `app.component.html`, `app.component.ts`

## Notes
- Branch empilhada sobre a #25 (`feat/25-chat-component-layout-signals-stream-rendering`) porque o `ChatComponent` ainda não estava na `main` quando a issue começou — mergear a #25 antes (ou junto) desta PR.
- Decisão: raiz `''` → `/chat` (chat como página principal); home preservada em `/home` para consulta.
- Validação: 7 testes de rota/app shell passando + `ng build` sem erros.
