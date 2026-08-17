---
tutorial_part: 5
source_title: "Custom Catalogs in A2UI: Your Own Components for AI-Generated UIs"
source_url: https://www.angulararchitects.io/en/blog/custom-catalogs-in-a2ui-your-own-components-for-ai-generated-uis/
source_series: "Agentic UI with Angular (Angular Architects) — artigo 7 de 10"
status: draft
last_updated: 08-17-2026
---

# Tutorial A2UI — Parte 5: catálogos customizados em A2UI

> Documento agnóstico: escrito para ser lido tanto por humanos quanto por outras IAs que venham a continuar este trabalho no projeto A2UI. Cada passo abaixo tem uma issue equivalente no GitHub.

## 1. Resumo geral

Até a Parte 3, o projeto só usou o `BasicCatalog` padrão do SDK A2UI (`Text`, `Card`, `Column`, `Button`, etc.) — nunca um componente próprio da aplicação. Este artigo mostra como estender o A2UI com **catálogos customizados**: componentes Angular específicos do domínio (no artigo original, um widget de progresso de milhas de passageiro aéreo — `MilesProgress`) que o LLM pode referenciar num `updateComponents` do mesmo jeito que referencia `Text`/`Card`, com o mesmo mecanismo de data binding via `{ path }`.

Um componente customizado é: (1) um componente Angular normal, recebendo os dados via um input `props` tipado (`BoundProperty<T>`, que pode ser um valor concreto ou um binding); (2) um schema Zod que valida tanto o contrato do componente quanto o payload gerado pelo LLM; (3) registrado num `BasicCatalogBase` customizado (`extraComponents`), fornecido via `A2UI_RENDERER_CONFIG` ao lado (ou no lugar) do `BasicCatalog`. O artigo também cobre como avisar o agente sobre os componentes disponíveis (via `AG-UI context entries`) e um cuidado de segurança (`sendCatalogDescription`, pra não vazar a descrição completa do catálogo pro prompt sem necessidade — risco de prompt injection).

### Por que isso importa para o A2UI (o projeto)

O domínio de clima já estabelecido (`WeatherToolResult`) só usa `Text` genérico até agora — um componente customizado (ex: um indicador visual de umidade) é o primeiro caso em que o catálogo do projeto deixa de ser só o que o SDK já oferece.

## 2. Conceitos-chave do artigo

| Conceito | O que é |
|---|---|
| `BoundProperty<T>` | Tipo do valor de uma prop de componente customizado: ou um valor concreto, ou `{ path: '...' }` (binding pro data model) |
| `AngularComponentImplementation` | Interface que empacota `name` (tipo do componente no A2UI), `component` (classe Angular) e `schema` (Zod) — a "entrada" do catálogo |
| `BasicCatalogBase` | Classe usada para instanciar um catálogo customizado: `id`, `extraComponents`, `functions` |
| `zodToJsonSchema` | Converte o schema Zod do componente pra JSON Schema, formato que é transmitido ao LLM |
| `createFunctionImplementation` | Factory pra registrar uma função customizada chamável de dentro de um binding (`{ call, args, returnType }`), além de componentes |
| `A2UI_CUSTOM_CATALOG` | Injection token client-side que guarda o descritor do catálogo customizado, consumido na hora de avisar o agente |

## 3. Passos didáticos e issues equivalentes

Convenção: `-GOOGLE-A2UI-` para a mecânica de catálogo customizado do protocolo (existiria em qualquer projeto A2UI), `-A2UI-` para o uso específico do widget dentro do card de clima deste projeto.

### Passo 1 — Definir um componente customizado de clima (`HumidityGauge`)
Criar um componente Angular `standalone`, `OnPush`, com um input `props` tipado (`{ humidity: BoundProperty<number> }`), computed signals derivando o que for necessário pra exibição (ex: nível — "baixa"/"moderada"/"alta"), e um schema Zod (`humidityGaugeSchema`) usando o helper `binding(...)` pro campo `humidity`. Empacotar como `AngularComponentImplementation` (`humidityGaugeEntry`), seguindo o padrão do `MilesProgress` do artigo.

- **Issue:** [#75 — `[Front] -GOOGLE-A2UI- Define a custom weather widget component with Zod schema + binding()`](https://github.com/doljak-projects/A2UI_A17_Python/issues/75)

### Passo 2 — Registrar um catálogo customizado
Instanciar um `BasicCatalogBase` próprio do projeto (`id` distinto do catálogo padrão, `extraComponents: [humidityGaugeEntry]`), e fornecê-lo via `A2UI_RENDERER_CONFIG` — ao lado do `BasicCatalog` da issue #52 (o SDK suporta múltiplos catálogos registrados simultaneamente; `createSurface.catalogId` decide qual usar).

- **Issue:** [#76 — `[Front] -GOOGLE-A2UI- Register a custom catalog via BasicCatalogBase + A2UI_RENDERER_CONFIG`](https://github.com/doljak-projects/A2UI_A17_Python/issues/76)

### Passo 3 — Usar o widget customizado no card de clima
Trocar o `Text` de umidade (`card-humidity`, issue #54) por uma referência ao novo componente (`{ id: 'card-humidity', component: 'HumidityGauge', humidity: { path: '/humidity' } }`) em `createWeatherCard()`, apontando `createSurface.catalogId` pro catálogo customizado. Validação visual: o card em `/a2ui-test` passa a renderizar o gauge em vez do número cru.

- **Issue:** [#77 — `[Front] -A2UI- Wire the custom widget into the weather card's component tree`](https://github.com/doljak-projects/A2UI_A17_Python/issues/77)

## 4. O que fica para depois

O artigo também cobre como avisar o **agente** sobre os componentes customizados disponíveis (`connectAgentContext`/`catalogToContextEntry`, injetando a descrição do catálogo no system prompt via `addCustomCatalogInstructions` no lado servidor) — isso só faz sentido quando o LLM está gerando a estrutura A2UI livremente, o que ainda não é o caso deste projeto (o `WeatherToolCallAgent` monta o card de forma determinística). Fica registrado como pré-requisito futuro, junto com a nota equivalente da Parte 4.
