---
issue: 55
title: "[Front] -GOOGLE-A2UI- Handle a client action to refresh the weather card in place"
branch: feat/a2ui-weather-refresh-55-onaction
status: closed
last_updated: 08-17-2026
---

# Issue #55 — Handle a client action to refresh the weather card in place

## Objective
Adicionar um `Button` ao card de clima (issue #54) com uma ação nomeada (`refreshWeather`), assinar `renderer.surfaceGroup.onAction` e emitir uma nova `updateDataModel` com dado mockado atualizado — sem recriar a surface (sem novo `createSurface`).

## Scope
- Adicionar um componente `Button` ao card do A2UI (issue #53/#54), com `action: { event: { name: 'refreshWeather' } }` (schema confirmado em `ButtonApi` — ver Decisões abaixo)
- Assinar `renderer.surfaceGroup.onAction` no componente da rota de demo (`/a2ui-test`) para capturar a ação disparada pelo botão
- Ao receber a ação `refreshWeather`, montar uma nova mensagem `updateDataModel` com dados de clima mockados diferentes dos iniciais, atualizando o card no lugar
- Cuidado de ciclo de vida: `onAction` **não é um Observable RxJS** — o cleanup da assinatura é manual, via `DestroyRef`
- Reference: `docs/tutorial_A2UI/03-google-a2ui-dynamic-ui.md` (Passo 4)

## Nota sobre a base da branch
A issue #54 foi fechada no GitHub, mas o commit `7e702f7` (`feat: model A2UI weather card using existing WeatherToolResult shape`, branch `feat/a2ui-weather-card-54-weathertoolresult`) **ainda não foi mergeado em `main`** — não há PR mergeado. Como a #55 depende diretamente do card de clima da #54 (`createWeatherCard()` em `a2ui-weather-card.ts`), a branch `feat/a2ui-weather-refresh-55-onaction` foi criada a partir do commit da #54, não da `main`. Fica pendente abrir/mergear o PR da #54 antes (ou junto) do PR da #55, senão o PR da #55 vai incluir o diff inteiro da #54 também.

## Investigação do SDK (`@a2ui/web_core@0.10.6`, `src/v0_9`)

- **`ButtonApi.schema` (`basic_catalog/components/basic_components.d.ts`):** `Button` tem `child` (string, ID do conteúdo), `variant` opcional e `action: { event: { name: string, context?: Record<string, string|number|boolean|any[]|{path}|{call,args,returnType}> } }`. Ou seja, a ação vai dentro de `action.event`, não direto em `action.name` como eu supunha antes de checar — o wrapper `event` é obrigatório.
- **`A2uiClientActionSchema` (`schema/client-to-server.d.ts`):** o que chega de volta em `onAction` é `{ name, surfaceId, sourceComponentId, timestamp, context }` — mensagem "achatada", sem o wrapper `event` (esse é só na declaração do botão, não no evento emitido).
- **`SurfaceGroupModel.onAction` (`state/surface-group-model.d.ts`):** tipado como `EventSource<A2uiClientAction>`, dispara pra ações de **qualquer** surface do grupo (não filtra por `surfaceId` sozinho — se houver mais de uma surface ativa, o handler precisa checar `action.surfaceId`/`action.name`).
- **`EventSource<T>` (`common/events.d.ts`):** confirma que **não é RxJS** — é um emitter próprio: `.subscribe(listener)` devolve um `Subscription` com `.unsubscribe()`. Cleanup correto: guardar a `Subscription` e chamar `.unsubscribe()` num `DestroyRef.onDestroy(...)`, não `takeUntilDestroyed()`.
- **Shape real usado no código (não o zod schema bruto):** confirmado em `a2ui-simple-card.ts`/`a2ui-weather-card.ts` que os itens de `updateComponents.components` são achatados — `{ id, component: '<Tipo>', ...propriedades }` — sem wrapper `componentProperties`. O `Button` deve seguir o mesmo padrão: `{ id: 'refresh-btn', component: 'Button', child: '<id-do-texto>', action: { event: { name: 'refreshWeather' } } }`.

## Decisões de implementação

- **`REFRESH_WEATHER_ACTION` como constante exportada em `a2ui-weather-card.ts`**, em vez de string literal duplicada no componente e no helper. Evita divergência entre o `name` declarado no `Button.action.event` e o `name` checado no handler de `onAction`.
- **Novo componente `Button` incluído dentro de `createWeatherCard()`**, como último filho da `Column` (`refresh-button`), com um `Text` próprio (`refresh-button-label`, texto "Atualizar") como `child` — seguindo o mesmo padrão de referência-por-ID do `Card.child`/`Column.children` (issue #53). Não criei uma função separada só pro botão: ele faz parte do card desde a criação (mesma mensagem `updateComponents`), então entra na função existente.
- **`refreshWeatherCardData(surfaceId, data)` como função nova**, devolvendo só a mensagem `updateDataModel` (sem `createSurface`/`updateComponents`) — é literalmente o "no lugar" que a issue pede: reenviar o data model não recria nem re-renderiza a árvore de componentes, só atualiza os valores nos `path`s já bindados.
- **Handler de `onAction` filtra por `action.surfaceId` E `action.name`** antes de agir, mesmo só havendo uma surface ativa no momento — `onAction` do SDK dispara pra qualquer surface do grupo (confirmado na investigação acima), então o filtro evita acoplar o comportamento a "só existe uma surface por enquanto".
- **Mock de refresh: alterna entre duas cidades fixas (`Rio de Janeiro`/`São Paulo`) via um índice local no componente**, reaproveitando `buildMockWeatherResult(city)` já existente (issue #36/#48) em vez de criar um gerador de dado novo. Como `buildMockWeatherResult` retorna sempre os mesmos `temperature_c`/`description`/`humidity` (só o `city` varia pelo argumento), trocar a cidade é a forma mais simples de tornar visível que o card foi atualizado, sem inventar lógica de mock nova nem tocar no arquivo de domínio (`weather-tool-for-a2ui.ts`) — mantém o escopo da issue restrito à mecânica do protocolo, não ao realismo do dado.
- **`this.destroyRef.onDestroy(() => subscription.unsubscribe())`** para o cleanup, confirmando a descoberta da investigação: `onAction` não é RxJS, então `takeUntilDestroyed()` não se aplica — o padrão usado é guardar a `Subscription` retornada por `.subscribe()` e chamar `.unsubscribe()` manualmente.

## Status
> Atualizado em: 08-17-2026

- [x] Worktree e branch criados (rebaseados sobre o commit da #54, não sobre `main`) e doc de spec criado.
- [x] SDK investigado: `Button.action`, `A2uiClientAction`, `SurfaceGroupModel.onAction`, `EventSource`/`Subscription`.
- [x] `Button` adicionado a `createWeatherCard()` (`a2ui-weather-card.ts`), com `REFRESH_WEATHER_ACTION` e `refreshWeatherCardData()` novos.
- [x] `A2uiTestComponent` assina `renderer.surfaceGroup.onAction`, filtra por `surfaceId`/`name`, alterna cidade mockada e reemite `updateDataModel`; cleanup via `DestroyRef`.
- [x] `ng build` limpo (só warning de budget pré-existente, mesmo teto citado nas issues #46/#53/#54). `ng test`: 46/49 verdes, mesmas 3 falhas pré-existentes de `chat.component.spec.ts`, sem regressão.
- [x] Verificação visual no browser (`ng serve`): clique em "Atualizar" alterna o card entre Rio de Janeiro/São Paulo in-place, sem recriar a surface; sem erros no console.

## Notes
- Reaproveita o helper/estrutura de componentes das issues #53/#54 — não recriou o card do zero.
- Pendência fora do escopo desta issue: mergear o PR da #54 em `main` (ver "Nota sobre a base da branch" acima) antes/junto do PR da #55.
