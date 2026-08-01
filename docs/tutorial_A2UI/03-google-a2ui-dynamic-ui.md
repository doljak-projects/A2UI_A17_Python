---
tutorial_part: 3
source_title: "A2UI: How AI Generates Dynamic UIs at Runtime"
source_url: https://www.angulararchitects.io/en/blog/a2ui-how-ai-generates-dynamic-uis-at-runtime/
source_series: "Agentic UI with Angular (Angular Architects) — artigo 5 de 10"
status: draft
last_updated: 2026-08-01
---

# Tutorial A2UI — Parte 3: o protocolo A2UI da Google (UI dinâmica em runtime)

> Documento agnóstico: escrito para ser lido tanto por humanos quanto por outras IAs que venham a continuar este trabalho no projeto A2UI. Cada passo abaixo tem uma issue equivalente no GitHub.

## ⚠️ Aviso de nomenclatura

Este artigo é sobre **A2UI da Google** — "Agent-to-UI", um protocolo/padrão que a Google introduziu para permitir que um LLM devolva **estruturas de UI inteiras**, não só texto. O nome **coincide** com o nome deste projeto ("A2UI", nosso design system Angular Material — ver `README.md`), mas são coisas diferentes e sem relação.

Pra não confundir os dois nas issues e nos docs, esta Parte 3 usa o marcador **`-GOOGLE-A2UI-`** (em vez do `-A2UI-` já usado nas Partes 1/2 pra "integração específica no projeto"). Quando um passo aqui reaproveitar algo do projeto A2UI (ex: o shape de `WeatherToolResult`), o marcador volta a ser `-A2UI-` normalmente — é só a mecânica do protocolo da Google que ganha o marcador novo.

## 1. Resumo geral

O protocolo A2UI da Google define um **vocabulário de componentes** predefinidos (o "catálogo") e um **formato de mensagens** pelo qual um agente descreve uma UI e o cliente a renderiza — sem o cliente precisar carregar/executar código estranho em runtime (diferente de abordagens tipo MCP Apps, onde o agente manda componentes prontos). O agente decide **o quê** mostrar; o cliente (com seu catálogo local) decide **como** renderizar.

Conceito central: uma **surface** é uma área lógica de exibição no cliente. O agente:
1. Cria a surface (`createSurface`)
2. Popula/atualiza os componentes dela (`updateComponents`)
3. Popula/substitui os dados que alimentam os componentes (`updateDataModel`)
4. Eventualmente remove a surface (`deleteSurface`)

O SDK Angular (`@a2ui/angular` + `@a2ui/web_core`, versão `v0_9`) processa essas mensagens e renderiza um `<a2ui-v09-surface>`. O artigo usa um exemplo de passageiro de voo (`Passenger` com `bonusMiles`); este tutorial adapta pro domínio de clima já estabelecido nas Partes 1/2 (`WeatherToolResult`, issue #35).

### Por que isso importa para o A2UI (o projeto)

Diferente das Partes 1/2 (que dependem do backend Python emitindo eventos AG-UI), esta Parte 3 é **inteiramente frontend** e autocontida — não depende de nenhum endpoint novo. É a base pra entender o protocolo A2UI da Google isoladamente, antes da Parte 6 do artigo original ("Integrating A2UI with AG-UI and CopilotKit in Angular") — que é o próximo artigo da série e deve virar a **Parte 4** deste tutorial: unir o que foi feito aqui com o agent store/CopilotKit da Parte 2.

## 2. Conceitos-chave do artigo

| Conceito | O que é |
|---|---|
| `A2uiMessage` | Interface de uma mensagem do protocolo (`@a2ui/web_core/v0_9`) |
| `createSurface` | Mensagem que cria uma surface lógica (`surfaceId`, `catalogId`) |
| `updateComponents` | Mensagem que adiciona/atualiza a árvore de componentes de uma surface |
| `updateDataModel` | Mensagem que insere/substitui dados no modelo de dados da surface (`path` + `value`) |
| `deleteSurface` | Mensagem que remove uma surface e seu conteúdo |
| `BasicCatalog` | Catálogo padrão do SDK: componentes de display (`Text`, `Image`, `Icon`...), layout (`Row`, `Column`, `List`...), container (`Card`, `Tabs`, `Modal`...) e input (`Button`, `TextField`, `Slider`...), além de funções (`formatNumber`, `required`, `and`/`or`, etc.) |
| `A2uiRendererService` | Serviço Angular que processa mensagens (`processMessages(messages)`) e expõe `surfaceGroup` |
| `SurfaceComponent` (`<a2ui-v09-surface>`) | Componente que renderiza uma surface pelo `surfaceId` |
| `A2uiClientAction` | Ação disparada por um componente de input (ex: um `Button`), capturada via `renderer.surfaceGroup.onAction` |
| Data binding (`{ path: '...' }`) | Componentes referenciam dados da surface por path, não por valor embutido |
| Chamada de função (`{ call, args, returnType }`) | Componentes podem chamar funções do catálogo (ex: `formatNumber`) inline no binding |

## 3. Passos didáticos e issues equivalentes

Convenção desta parte:
- **`-GOOGLE-A2UI-`** no título → mecânica do protocolo A2UI da Google em si (existiria em qualquer projeto que o adote).
- **`-A2UI-`** no título → integração específica no projeto A2UI (reaproveitando `WeatherToolResult`, etc.) — mesmo sentido das Partes 1/2.
- Todos os passos são `[Front]` — este artigo não tem componente de backend.

### Passo 1 — Instalar e configurar o SDK A2UI
Instalar `@a2ui/angular` e `@a2ui/web_core`, registrar `A2UI_RENDERER_CONFIG` (com `BasicCatalog`), `provideMarkdownRenderer(...)` (via `marked`) e `A2uiRendererService` nos providers da app. Sem renderizar nada ainda.

- **Issue:** [#52 — `[Front] -GOOGLE-A2UI- Install and configure the A2UI Angular SDK`](https://github.com/doljak-projects/A2UI_A17_Python/issues/52)

### Passo 2 — Renderizar um card estático via createSurface/updateComponents/updateDataModel
Implementar uma função helper que devolve `A2uiMessage[]` (uma `createSurface`, uma `updateComponents` descrevendo um `Card`, uma `updateDataModel` com os dados), processá-las via `renderer.processMessages(...)` e exibir via `<a2ui-v09-surface>`, numa rota de demo isolada (mesmo princípio de isolamento do `/agui-test`).

- **Issue:** [#53 — `[Front] -GOOGLE-A2UI- Render a static card via createSurface/updateComponents/updateDataModel`](https://github.com/doljak-projects/A2UI_A17_Python/issues/53)

### Passo 3 — Modelar o card de clima com o WeatherToolResult existente
Trocar o dataset genérico do Passo 2 pelo shape de clima já estabelecido na issue #35 (`city`/`temperature_c`/`description`/`humidity`), reaproveitando `weatherSchema`/`WeatherToolResult` em vez de duplicar um modelo novo.

- **Issue:** [#54 — `[Front] -A2UI- Model the A2UI weather card using the existing WeatherToolResult shape`](https://github.com/doljak-projects/A2UI_A17_Python/issues/54)

### Passo 4 — Ação do cliente pra atualizar o card no lugar
Adicionar um `Button` com uma ação nomeada (`refreshWeather`), assinar `renderer.surfaceGroup.onAction`, e emitir uma nova `updateDataModel` com dado mockado atualizado — sem recriar a surface. `onAction` não é um Observable RxJS, então o cleanup é manual via `DestroyRef`.

- **Issue:** [#55 — `[Front] -GOOGLE-A2UI- Handle a client action to refresh the weather card in place`](https://github.com/doljak-projects/A2UI_A17_Python/issues/55)

## 4. O que fica para depois

O artigo 6 da série ("Integrating A2UI with AG-UI and CopilotKit in Angular") une os três pedaços já cobertos: AG-UI (Partes 1/2), CopilotKit (Parte 2) e o protocolo A2UI da Google (esta Parte 3) — um agente real decidindo, via AG-UI, quando mandar mensagens A2UI pro cliente renderizar. Esse é o próximo tema natural a documentar como **Parte 4** deste tutorial, quando chegar a vez.
