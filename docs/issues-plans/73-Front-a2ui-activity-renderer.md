---
issue: 73
title: "[Front] -A2UI- Implement A2uiActivityRenderer via CopilotKit's ActivityRenderer interface"
branch: feat/a2ui-agui-integration-72-74-activity-snapshot
status: closed
last_updated: 08-18-2026
---

# Issue #73 — Implement A2uiActivityRenderer via CopilotKit's ActivityRenderer interface

## Objective
CopilotKit expõe uma interface `ActivityRenderer<T>` para componentes que renderizam um `activityType` customizado. Esta issue implementa um componente Angular que satisfaz essa interface para o `activityType: 'a2ui-surface'` introduzido na issue #72, montando o card A2UI já existente via o `A2uiRendererService` configurado na issue #52.

## Scope
- `components/a2ui-activity-renderer/a2ui-activity-renderer.component.ts` (novo): `A2uiActivityRenderer implements ActivityRenderer<A2uiSurfaceContent>`
- `extractSurfaceId()`: helper que varre `content.operations` procurando o primeiro `createSurface`/`updateComponents`/`updateDataModel` pra descobrir o `surfaceId`
- `a2uiSurfaceContentSchema` (Zod) validando `{ operations: A2uiMessage[] }`
- `a2uiActivityRendererConfig`: `RenderActivityMessageConfig<A2uiSurfaceContent>` mapeando `activityType: 'a2ui-surface'` → `A2uiActivityRenderer`
- `app.config.ts`: registrado via `provideCopilotKit({ renderActivityMessages: [a2uiActivityRendererConfig] })`
- Reference: `docs/tutorial_A2UI/04-integrating-a2ui-with-ag-ui.md` (Passo 2)

## Decisões de implementação
- **Um `effect()` no construtor, não um `ngOnInit`.** `processMessages(operations)` roda dentro de `effect(() => { ... this.content().operations ... })`, reagindo automaticamente se `content` mudar (novo snapshot chegando pro mesmo `activityType`) — sem exigir lifecycle hook manual.
- **`extractSurfaceId` varre as operações em vez de exigir um campo `surfaceId` fixo na mensagem de atividade**, porque o payload é genérico (`{ operations: A2uiMessage[] }`) — a única forma confiável de saber qual surface renderizar é inspecionar as próprias mensagens A2UI.
- **Validação via Zod (`a2uiSurfaceContentSchema`)** integrada ao contrato `RenderActivityMessageConfig.content.safeParse`, que o CopilotKit chama antes de montar o componente — payloads malformados não chegam a instanciar `A2uiActivityRenderer`.

## Status
> Atualizado em: 08-18-2026

- [x] `A2uiActivityRenderer` implementado, registrado via `provideCopilotKit({ renderActivityMessages: [...] })`.
- [x] **Validação funcional:** `ng build` limpo (orçamento de bundle ajustado pra 1.6 MB, ver `## Notes`). `ng test`: 47/50 verdes — as 3 falhas restantes são as pré-existentes e conhecidas de `chat.component.spec.ts`, sem relação com esta issue.
- [x] Integração ponta a ponta validada junto da issue #74 (mesmo PR).

## Notes
- **Orçamento de bundle (`angular.json`):** o teto `maximumError` de `apps/frontend/angular.json` foi ajustado de `1.5mb` pra `1.6mb` nesta issue — o baseline (antes de #72-74) já estava em 1.49 MB, a apenas 10 KB do teto anterior; o código novo desta issue (renderer + roteamento de atividade) empurrou o bundle inicial pra 1.56 MB. Decisão registrada aqui em vez de tentar lazy-loading (não é código exclusivo de uma rota isolada — o renderer precisa estar disponível globalmente, já que qualquer `ACTIVITY_SNAPSHOT` pode chegar a qualquer momento no chat).
- Implementado originalmente por sessão do Cursor (não commitado); esta issue documenta a versão reorganizada/validada em branch própria.
