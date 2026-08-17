---
issue: 53
title: "[Front] -GOOGLE-A2UI- Render a static card via createSurface/updateComponents/updateDataModel"
branch: feat/a2ui-static-card-53-createsurface
status: closed
last_updated: 08-17-2026
---

# Issue #53 — Render a static card via createSurface/updateComponents/updateDataModel

## Objective
Implementar o ciclo mínimo do protocolo A2UI da Google: uma função helper que devolve `A2uiMessage[]` (`createSurface` → `updateComponents` com um `Card` → `updateDataModel` com os dados), processado via `A2uiRendererService.processMessages(...)` e exibido através de `<a2ui-v09-surface>`, numa rota de demo isolada — mesmo princípio do `/agui-test` (issue #34).

## Scope
- Helper `createSimpleCard(surfaceId, catalogId, data)` em `core/services/a2ui-simple-card.ts`
- Rota `/a2ui-test` com componente que chama `processMessages(...)` no `ngOnInit` e renderiza `<a2ui-v09-surface [surfaceId]="surfaceId" />`
- Reference: `docs/tutorial_A2UI/03-google-a2ui-dynamic-ui.md` (Passo 2)

## Decisões de implementação

- **Componentes são referenciados por ID, não aninhados inline.** O array `components` de `updateComponents` é *flat* (confirmado no `.d.ts` do `@a2ui/web_core@0.10.6`, `server-to-client.d.ts`): `Card.child` é uma string de ID apontando pra outro item da mesma lista; `Column.children` é um array de IDs. A árvore é montada por referência, não por nesting no JSON. A estrutura usada: `Card` → `Column` → 2× `Text`.

- **`catalogId` não é `"basic"`, é a URL do catálogo.** Confirmado no `.mjs` do SDK (`BasicCatalogBase` constructor): o `id` default é `'https://a2ui.org/specification/v0_9/catalogs/basic/catalog.json'`. Em vez de hardcodar essa string no componente, o `id` é lido em runtime via `inject(BasicCatalog).id` (propriedade pública `readonly id: string` em `Catalog<T>`, `catalog/types.d.ts`) — evita duplicar/errar a URL se o SDK mudar o default.

- **Descoberta importante: a raiz da surface precisa ter `id: 'root'` literalmente.** Diferente do que se poderia supor (inferir a raiz pela árvore, ex.: o componente que não é filho de nenhum outro), `SurfaceComponent` (`<a2ui-v09-surface>`) usa por default `componentKey = input('root', ...)` (confirmado no `.mjs`, `a2ui-angular-v0_9.mjs:339`). Sem um componente com `id: 'root'` no array de `updateComponents`, a surface renderiza um `<a2ui-v09-component-host>` vazio, **sem nenhum erro no console** — foi preciso inspecionar o DOM (`document.querySelector('a2ui-v09-surface').childElementCount`) pra perceber que o host existia mas sem filhos. Corrigido trocando o `id` do `Card` de `'card'` para `'root'`.

- **Data binding via `{ path: '/...' }` em vez de string literal.** O `Text.text` do campo raiz aceita `DynamicString` (string | `{path}` | function call). Optei por usar o binding mesmo com dado estático, pra já ilustrar o mecanismo de `updateDataModel` que a issue pede explicitamente (as três mensagens do ciclo) — a #54 é quem troca o dataset genérico pelo shape de clima (`WeatherToolResult`).

- **`updateDataModel` sem `path` explícito.** Confirmado em `message-processor.js` (`processUpdateDataModelMessage`): `path` tem fallback pra `'/'` quando omitido, e `dataModel.set('/', value)` substitui a raiz inteira. Como o card só tem `title`/`subtitle`, mandar o objeto completo sem `path` é equivalente e mais simples do que declarar `path: '/'` manualmente.

## Status
> Atualizado em: 2026-08-17

- [x] Helper `createSimpleCard()` criado em `core/services/a2ui-simple-card.ts`, retornando as 3 mensagens (`createSurface`/`updateComponents`/`updateDataModel`).
- [x] Componente `A2uiTestComponent` (rota `/a2ui-test`) criado, chama `processMessages(...)` no `ngOnInit`, renderiza `<a2ui-v09-surface [surfaceId]="surfaceId" />`.
- [x] `ng build` limpo (só o warning de budget pré-existente, dentro do teto de 1.5 MB da issue #46). `ng test`: 46/49 verdes, mesmas 3 falhas pré-existentes de `chat.component.spec.ts`, sem regressão.
- [x] Verificação visual no browser (`ng serve`): card renderiza título/subtítulo corretamente após o fix do `id: 'root'`.

## Notes
- Dataset ainda genérico (`title`/`subtitle`) — a issue #54 troca pelo shape de clima (`WeatherToolResult`, issue #35), reaproveitando este mesmo helper/estrutura de componentes.
- Nenhuma ação de cliente (`Button`/`onAction`) ainda — isso é a issue #55.
