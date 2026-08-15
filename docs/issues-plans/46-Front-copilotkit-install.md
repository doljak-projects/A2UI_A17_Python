---
issue: 46
title: "[Front] -AG-UI- Install and configure CopilotKit for Angular"
branch: feat/copilotkit-install-46-provider
status: closed
last_updated: 08-15-2026
---

# Issue #46 — Install and configure CopilotKit for Angular

## Objective
Add `@copilotkit/angular` to the frontend workspace and register `provideCopilotKit({ defaultToolRendering: true })` in `app.config.ts`, laying the foundation for the more idiomatic agent integration shown in the tutorial — replacing the hand-rolled `AguiAgentService`/`AgentSubscriber` boilerplate of issues #34–#36. No agent wired up yet.

## Scope
- Install `@copilotkit/angular` (and required peer deps) in `apps/frontend`
- Add `provideCopilotKit({ defaultToolRendering: true })` to `app.config.ts`
- Confirm the app still builds and serves correctly with the provider in place
- Reference: `docs/tutorial_A2UI/02-ag-ui-copilotkit-angular.md` (Passo 2)

## Status
> Atualizado em: 2026-08-15

- [x] Worktree `wts/46-worktree-copilotkit-install` (branch `feat/copilotkit-install-46-provider`) já existia de uma sessão anterior; tinha só um `package-lock.json` modificado, sem relação com a issue (nada de `@copilotkit` no `package.json` nem no `node_modules`) — descartado (`git checkout --`) por decisão do usuário antes de começar.
- [x] `@copilotkit/angular@0.3.1` instalado via `npm install @copilotkit/angular --workspace apps/frontend`. Confirmado via `npm view` que seus peer deps (`@angular/core`/`common`/`cdk` `^20 || ^21 || ^22`) satisfazem o Angular 21.2.19 já em uso (issue #59). Diff final ficou limpo: 1 linha em `package.json` + o delta correspondente no lockfile.
- [x] `provideCopilotKit({ defaultToolRendering: true })` adicionado ao array `providers` de `apps/frontend/src/app/app.config.ts`.
- [x] `ng build` falhou inicialmente por orçamento de bundle excedido (bundle subiu de ~480 kB pra 1.20 MB com o CopilotKit — budget `initial` era `maximumError: 1mb`). Ajustado em `angular.json` pra `maximumWarning: 1mb` / `maximumError: 1.5mb`. Build limpo depois disso (só warnings pré-existentes de dependências CommonJS internas do CopilotKit — `@jetbrains/websandbox`, `partial-json`, `chalk`, `node-fetch` — sem impacto funcional).
- [x] `ng test` — 36/39 verdes; as 3 falhas são as mesmas pré-existentes em `agui-test.component.spec.ts` (não relacionadas a esta issue), sem regressão nova.

## Notes
- Nenhum agente foi ligado ao provider nesta issue — isso é a issue #47 (`AppHttpAgent` + `initAgentStore` + `injectAgentStore`), que consumirá o endpoint `POST /api/agui/weather-tool-agent-demo` da issue #45.
- O aumento do budget de bundle é esperado ao adicionar um SDK desse porte; se outras dependências grandes entrarem nas próximas issues (#47–#50), pode valer revisitar o valor de novo.
