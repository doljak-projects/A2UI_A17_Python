---
issue: 52
title: "[Front] -GOOGLE-A2UI- Install and configure the A2UI Angular SDK"
branch: feat/a2ui-sdk-install-52-provider
status: closed
last_updated: 08-15-2026
---

# Issue #52 — Install and configure the A2UI Angular SDK

## Objective
Install Google's A2UI SDK (`@a2ui/angular` + `@a2ui/web_core`) and wire the Angular providers needed to render A2UI surfaces (renderer service, basic component catalog, Markdown support) — no rendering yet, just the SDK in place. Foundation for issues #53–#55.

**Nota de nomenclatura:** este "A2UI" é o protocolo Agent-to-UI da Google — vocabulário de componentes + formato de mensagens pra um agente descrever UI dinâmica. Não tem relação com o nome do projeto (design system Angular Material A2UI). Issues desta trilha usam o marcador `-GOOGLE-A2UI-` pra não confundir com o `-A2UI-` de integração específica do projeto (Partes 1/2). Ver `docs/tutorial_A2UI/03-google-a2ui-dynamic-ui.md`.

## Scope
- Install `@a2ui/angular` and `@a2ui/web_core` in `apps/frontend`
- Register `A2UI_RENDERER_CONFIG` (providing `BasicCatalog`), `provideMarkdownRenderer(...)`, and `A2uiRendererService` in the app providers
- Confirm the app still builds and serves correctly with the providers in place
- Reference: `docs/tutorial_A2UI/03-google-a2ui-dynamic-ui.md` (Passo 1)

## Decisões de arquitetura
- **`@a2ui/markdown-it` instalado também**, além dos dois pacotes citados no tutorial. Conferido no `.mjs` do SDK: `DefaultMarkdownRenderer` (usado quando `provideMarkdownRenderer()` é chamado sem argumento) faz `await import('@a2ui/markdown-it')` como dependência **opcional** — sem o pacote, cai num fallback com `console.warn`. Instalar evita esse warning em runtime, sem custo (peer dep declarado pelo próprio `@a2ui/angular`).
- **Import via subpath `@a2ui/angular/v0_9`**, não do root `@a2ui/angular`. Confirmado no `package.json` do pacote (`exports`): o root `.` aponta pra um bundle genérico, mas `A2UI_RENDERER_CONFIG`/`BasicCatalog`/`provideA2Ui`/`provideMarkdownRenderer` estão nos subpaths versionados (`./v0_9`, `./v0_8`). O tutorial usa a v0.9, versão mais recente do protocolo.
- **`provideA2Ui(...)`, não um provider `A2UI_RENDERER_CONFIG` cru**: o SDK expõe uma função helper (`provideA2Ui({ catalogs, actionHandler? })`) que já monta o `InjectionToken` corretamente — usá-la em vez de instanciar o provider manualmente evita depender de detalhes internos do token.
- **`A2uiRendererService` não precisa provider explícito**: é `providedIn: 'root'` (confirmado no `.d.ts`), injetável direto via `inject(A2uiRendererService)` sem entrada no array `providers`.

## Status
> Atualizado em: 2026-08-15

- [x] `@a2ui/angular@0.10.5`, `@a2ui/web_core@0.10.6` e `@a2ui/markdown-it@0.1.1` instalados em `apps/frontend`. Peer deps (`@angular/core`/`common`/`platform-browser` `^21.2.5`) confirmados compatíveis com o Angular 21.2.19 já em uso.
- [x] `app.config.ts` estendido: `provideA2Ui({ catalogs: [new BasicCatalog()] })` + `provideMarkdownRenderer()` adicionados ao array `providers`, ao lado do `provideCopilotKit` (issue #46).
- [x] `ng build` limpo — bundle subiu de 1.20 MB pra 1.29 MB (ainda dentro do teto de `1.5mb` ajustado na issue #46; só o warning de budget de sempre, sem erro). `ng test`: 41/44 verdes, mesmas 3 falhas pré-existentes de `agui-test.component.spec.ts`, sem regressão nova.

## Notes
- Nenhuma surface é renderizada ainda — isso é a issue #53 (card estático via `createSurface`/`updateComponents`/`updateDataModel`), que consome `A2uiRendererService` e `<a2ui-v09-surface>` diretamente.
- Esta trilha (Parte 3 do tutorial) é inteiramente frontend e independente das issues #49/#50 (Parte 2, CopilotKit) — nenhum arquivo em comum, sem risco de conflito.
