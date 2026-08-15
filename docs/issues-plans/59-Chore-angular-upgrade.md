---
issue: 59
title: "[Front] [Chore] Upgrade Angular from 17 to 21 (unblocks CopilotKit/A2UI Angular SDKs)"
branch: chore/angular-upgrade-59-17-to-22
status: in-progress
last_updated: 2026-08-15
---

# Issue #59 — Upgrade Angular from 17 to 21 (unblocks CopilotKit/A2UI Angular SDKs)

## Objective
None of the official Angular SDKs needed for Tutorial A2UI Parts 2 and 3 (`@copilotkit/angular`, `@a2ui/angular`) support Angular 17, the version this project is currently on. `@copilotkit/angular` requires Angular `^20.0.0 || ^21.0.0 || ^22.0.0`. `@a2ui/angular` requires Angular `^21.2.5`. Target is **Angular 21** (latest patch, `21.2.19`) — satisfies both SDKs' peer ranges, no need to go further to 22 right now.

## Scope
- Upgrade `apps/frontend` through each major sequentially: 18 → 19 → 20 → 21, running `ng update` (core + cli + material + cdk in lockstep) at each step
- Resolve breaking changes/deprecations surfaced by each step's automated migrations
- Re-verify existing AG-UI demo pages (issues #34–#45) and base chat (issues #24–#26) still build, serve and pass tests after the final upgrade
- Re-attempt installing `@copilotkit/angular` and `@a2ui/angular` once on Angular 21, confirming issues #46 and #52 are unblocked

## Modo de trabalho desta issue
Mesmo formato mentorado das demais: conceito explicado antes de cada passo, confirmação do usuário, só então a execução. Decisões registradas neste doc.

## Status
> Atualizado em: 2026-08-15

- [x] Passo 0 — Baseline (Angular 17.3): `ng test` 36/39 (mesmas 3 falhas pré-existentes de `chat.component.spec.ts`), `ng build` limpo (bundle inicial 451.60 kB).
- [x] Passo 1 — 17 → 18 (`ng update @angular/core@18 @angular/cli@18 @angular/material@18`). Migrations automáticas aplicadas: Angular CDK/Material atualizados; `styles.scss` migrado pra API M2 renomeada (`mat.define-palette` → `mat.m2-define-palette`, etc.). Build e `ng test` (36/39, mesmas 3 falhas pré-existentes) confirmados no Angular 18.2.21.
- [x] Passo 2 — 18 → 19 (`ng update @angular/core@19 @angular/cli@19 @angular/material@19`). Migrations automáticas aplicadas: remoção de `standalone: true` redundante em 4 componentes; `styles.scss` — `mat.core()` substituído por `mat.elevation-classes()` + `mat.app-background()`; CDK/Material em `^19.2.x`, TypeScript `~5.8.3`, zone.js `~0.15.1`. Reinstall de `node_modules`/lockfile necessário pra resolver `@angular/animations` ausente. Build limpo (bundle inicial 473.22 kB) e `ng test` 36/39 confirmados; smoke test em `/`, `/chat`, `/agui-test` ok.
- [ ] Passo 3 — 19 → 20
- [ ] Passo 4 — 20 → 21
- [ ] Passo 5 — Validação final: build, testes, `/agui-test` funcional; instalar `@copilotkit/angular`/`@a2ui/angular` de teste pra confirmar que resolvem

## Notes
- Backend (Python) não é afetado por esta issue.
- `@angular/cdk`/`@angular/material` sobem em lockstep com `@angular/core` a cada passo (mesma versão major).
- `node_modules`/lockfile mudam bastante nesta issue — normal, não é escopo indevido.
