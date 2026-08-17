---
tutorial_part: 4
source_title: "Integrating A2UI with AG-UI and CopilotKit in Angular"
source_url: https://www.angulararchitects.io/en/blog/integrating-a2ui-with-ag-ui-in-angular/
source_series: "Agentic UI with Angular (Angular Architects) — artigo 6 de 10"
status: draft
last_updated: 08-17-2026
---

# Tutorial A2UI — Parte 4: integrando A2UI com AG-UI e CopilotKit

> Documento agnóstico: escrito para ser lido tanto por humanos quanto por outras IAs que venham a continuar este trabalho no projeto A2UI. Cada passo abaixo tem uma issue equivalente no GitHub.

## 1. Resumo geral

As Partes 1/2 (AG-UI + CopilotKit) e a Parte 3 (protocolo A2UI da Google) foram construídas isoladamente até aqui: a Parte 3 renderiza um card de clima numa rota de demo (`/a2ui-test`) chamando `renderer.processMessages(...)` manualmente, sem nenhum agente real envolvido. Este artigo fecha essa lacuna, mostrando como um agente real — via transporte AG-UI — decide **quando** mandar mensagens A2UI para o cliente renderizar, dentro do chat de verdade.

O mecanismo: como o AG-UI não define transporte oficial para mensagens A2UI, o artigo propõe embutir as operações A2UI (`createSurface`/`updateComponents`/`updateDataModel`) dentro de um evento AG-UI `ACTIVITY_SNAPSHOT`, com um campo `activityType` customizado (ex: `'a2ui-surface'`) para identificar o payload. O servidor valida a estrutura A2UI gerada pelo LLM via uma tool call antes de emitir o snapshot — evitando mandar markup inválido pro cliente. No Angular, o CopilotKit já tem um mecanismo de `ActivityRenderer` para esse tipo de mensagem: basta registrar um componente que implementa essa interface, extrai o `surfaceId` das operações recebidas e delega pro `A2uiRendererService` já configurado na Parte 3.

### Por que isso importa para o A2UI (o projeto)

É o primeiro ponto em que as três peças construídas separadamente (agente AG-UI real, CopilotKit, protocolo A2UI da Google) se conectam de ponta a ponta — o card de clima passa a ser decidido e emitido pelo agente de verdade, dentro do chat sidecar já existente (issue #50), em vez de ser hardcoded numa rota isolada.

## 2. Conceitos-chave do artigo

| Conceito | O que é |
|---|---|
| `ACTIVITY_SNAPSHOT` | Tipo de mensagem AG-UI que carrega um payload de "atividade" arbitrário, identificado por `activityType` |
| `ActivityRenderer<T>` | Interface do CopilotKit para componentes que renderizam um `activityType` específico (inputs: `content`, `activityType`, `message`, `agent`) |
| `RenderActivityMessageConfig<T>` | Config que mapeia um `activityType` para o componente `ActivityRenderer` e o schema de validação |
| `renderActivityMessages` | Opção de `provideCopilotKit(...)` que registra a lista de `RenderActivityMessageConfig` da app |
| Validação server-side via tool | O agente usa uma tool (chamada pelo próprio LLM) que valida a estrutura A2UI gerada e devolve erro pro LLM tentar de novo, antes de qualquer coisa chegar ao cliente |
| `<app-copilot-activity>` | Componente próprio da app que roteia uma mensagem `role: 'activity'` pro `ActivityRenderer` certo, com base no `activityType` |

## 3. Passos didáticos e issues equivalentes

Convenção desta parte: `-AG-UI-` para a mecânica de transporte (o snapshot em si), `-A2UI-` para a integração específica do projeto (o card de clima reaproveitado dentro do chat real).

### Passo 1 — Emitir operações A2UI dentro de um ACTIVITY_SNAPSHOT do agente de clima
No backend (`WeatherToolCallAgent`, issue #33), montar as mesmas operações A2UI já usadas no frontend (`createSurface`/`updateComponents`/`updateDataModel` do card de clima — issue #54) e emiti-las como conteúdo de um evento AG-UI `ACTIVITY_SNAPSHOT`, com `activityType: 'a2ui-surface'`. Sem validação via tool call ainda (fica pro Notes/próxima iteração) — o foco deste passo é só o transporte funcionar ponta a ponta.

- **Issue:** [#72 — `[Back] -AG-UI- Emit A2UI operations wrapped in an AG-UI ACTIVITY_SNAPSHOT from the weather agent`](https://github.com/doljak-projects/A2UI_A17_Python/issues/72)

### Passo 2 — Renderer de atividade A2UI no Angular (`A2uiActivityRenderer`)
Implementar um componente Angular que satisfaz `ActivityRenderer<A2uiSurfaceContent>`: recebe o `content.operations` do snapshot, extrai o `surfaceId` (primeira operação com `createSurface`/`updateComponents`/`updateDataModel`), chama `A2uiRendererService.processMessages(operations)` num `effect()`, e renderiza `<a2ui-v09-surface [surfaceId]="surface" />`. Registrar via `provideCopilotKit({ renderActivityMessages: [a2uiActivityRendererConfig] })`, ao lado do `A2UI_RENDERER_CONFIG`/`BasicCatalog`/`provideMarkdownRenderer` já configurados na issue #52.

- **Issue:** [#73 — `[Front] -A2UI- Implement A2uiActivityRenderer via CopilotKit's ActivityRenderer interface`](https://github.com/doljak-projects/A2UI_A17_Python/issues/73)

### Passo 3 — Renderizar o card de clima dentro do chat real
Atualizar o template de mensagens do chat sidecar (issue #50) para detectar `message.role === 'activity'` e delegar pro `<app-copilot-activity>`, fechando o ciclo: usuário manda mensagem no chat → agente decide mostrar o clima → emite o `ACTIVITY_SNAPSHOT` → `A2uiActivityRenderer` monta o card real dentro da conversa. A rota `/a2ui-test` (issue #53/#54/#55) continua existindo como demo isolada, mas o card passa a também aparecer no fluxo de produção.

- **Issue:** [#74 — `[Front] -A2UI- Render the weather card inside the real chat via the activity renderer`](https://github.com/doljak-projects/A2UI_A17_Python/issues/74)

## 4. O que fica para depois

O artigo original também cobre a validação server-side via tool call (o agente pede pro LLM gerar A2UI, valida a estrutura, e só então emite o snapshot — com retry em caso de erro) — este tutorial não reproduz essa parte porque o `WeatherToolCallAgent` atual monta o card de forma determinística (sem o LLM gerar a estrutura A2UI diretamente). Fica registrado aqui como possível "Parte 4.1" caso o projeto evolua pra ter o LLM gerando markup A2UI livremente (pré-requisito natural pra Parte 6, que também depende de geração de estrutura via LLM).
