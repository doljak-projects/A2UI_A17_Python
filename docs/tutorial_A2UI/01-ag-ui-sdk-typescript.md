---
tutorial_part: 1
source_title: "AG-UI in Practice: The SDK for TypeScript"
source_url: https://www.angulararchitects.io/en/blog/ag-ui-in-practice-the-sdk-for-typescript/
source_series: "Agentic Angular (Angular Architects) — parte 2 da série original"
status: draft
last_updated: 07-27-2026
---

# Tutorial A2UI — Parte 1: O SDK TypeScript do AG-UI na prática

> Documento agnóstico: escrito para ser lido tanto por humanos quanto por outras IAs que venham a continuar este trabalho no projeto A2UI. Cada passo abaixo tem uma issue equivalente no GitHub.

## 1. Resumo geral

O **AG-UI** é um protocolo que define as **mensagens semânticas trocadas entre um cliente (UI) e um agente de IA** — coisas como "a resposta começou", "chegou um pedaço de texto", "o agente quer chamar uma ferramenta", "a execução terminou". O protocolo por si só não diz *como* transportar essas mensagens (HTTP, SSE, WebSocket...); ele só define o **formato** das mensagens.

O artigo original mostra como usar o **SDK oficial TypeScript** (`@ag-ui/client`, `@ag-ui/core`) para:

1. Implementar, no lado do agente ("servidor"), uma classe que estende `AbstractAgent` e emite eventos AG-UI (início de execução, pedaços de texto, chamadas de ferramenta, fim de execução).
2. Consumir esses eventos no lado do cliente ("Angular") usando `HttpAgent` (transporte via SSE sobre HTTP) e um `AgentSubscriber` (handlers para cada tipo de evento).
3. Diferenciar **tools executadas no servidor** (o agente chama e resolve sozinho) de **tools executadas no cliente** (o navegador executa e devolve o resultado no próximo *run*).

O exemplo do artigo usa um domínio fictício chamado *Flight Weather* (clima para voos), com uma classe `FlightWeatherAgent` retornando dados de tempo para Frankfurt. Neste tutorial adaptamos esse exemplo ao **contexto real do A2UI**: o projeto já tem uma tool de clima (`get_weather`, ver `apps/backend/app/tools/weather.py`, issue #5) e um chat com streaming SSE (`ChatService`, issue #24). A sintaxe dos códigos do SDK (`AbstractAgent`, `EventType`, `HttpAgent`, `AgentSubscriber`, `Tool`) é mantida **exatamente como no artigo** — só o conteúdo de exemplo (nomes de classe, cidade, narrativa) é adaptado para a POC.

### Por que isso importa para o A2UI

Hoje o A2UI conversa com o LLM via `POST /api/chat` (SSE cru, eventos `text_delta`/`message_stop`/`error` definidos ad-hoc pelo próprio projeto — ver issue #3 e #24). O AG-UI **padroniza** esse contrato de eventos (`RUN_STARTED`, `TEXT_MESSAGE_START/CONTENT/END`, `TOOL_CALL_START/ARGS/END/RESULT`, `RUN_FINISHED`) e oferece SDKs prontos dos dois lados. Este tutorial é o primeiro passo para avaliar/adotar esse padrão no projeto, sem descartar o que já existe — os dois podem conviver enquanto exploramos.

## 2. Conceitos-chave do artigo

| Conceito | Lado | O que é |
|---|---|---|
| `AbstractAgent` | Servidor | Classe base que se estende para implementar um agente; o método `run(input)` retorna um `Observable<BaseEvent>` |
| `EventType` | Ambos | Enum dos tipos de evento AG-UI (`RUN_STARTED`, `TEXT_MESSAGE_*`, `TOOL_CALL_*`, `RUN_FINISHED`, etc.) |
| `HttpAgent` | Cliente | Implementação de transporte pronta que fala com o agente via HTTP + SSE |
| `AgentSubscriber` | Cliente | Objeto com um handler por tipo de evento (`onRunStartedEvent`, `onTextMessageContentEvent`, ...) |
| `Tool` (+ Zod) | Cliente | Descreve, em JSON Schema, uma ferramenta que o **cliente** sabe executar |
| Server-side tool call | Servidor | O próprio agente executa a tool e devolve o resultado ao LLM na mesma run |
| Client-side tool call | Cliente | O agente pede a execução; o cliente executa e devolve o resultado numa **nova run** |

## 3. Passos didáticos e issues equivalentes

Cada passo abaixo corresponde a uma issue no GitHub. A convenção de nomenclatura usada é:

- **`-AG-UI-`** no título → o passo trata da mecânica do **protocolo/SDK** em si (algo que existiria em qualquer projeto que adote AG-UI).
- **`-A2UI-`** no título → o passo trata da **integração desse mecanismo especificamente no projeto A2UI** (reaproveitando `get_weather`, `ChatService`, etc.).
- Prefixo `[Back]` ou `[Front]` indica se o trabalho é no `apps/backend` ou `apps/frontend`.

### Passo 1 — [Back] Esqueleto do agente AG-UI emitindo eventos de execução
Implementar uma classe que estende `AbstractAgent` e, no método `run(input)`, emite a sequência mínima de eventos de um turno de conversa: `RUN_STARTED` → `TEXT_MESSAGE_START` → `TEXT_MESSAGE_CONTENT` (um ou mais deltas) → `TEXT_MESSAGE_END` → `RUN_FINISHED`. Sem chamar nenhum LLM ainda — só validar o formato dos eventos, como o artigo faz.

- **Issue:** [#32 — `[Back] -AG-UI- Agent skeleton emitting RUN_STARTED/TEXT_MESSAGE/RUN_FINISHED events`](https://github.com/doljak-projects/A2UI_A17_Python/issues/32)

### Passo 2 — [Back] Tool call de clima executada no servidor
Estender o agente do Passo 1 para, dentro do mesmo `run`, emitir uma chamada de tool server-side (`TOOL_CALL_START` → `TOOL_CALL_ARGS` → `TOOL_CALL_END`), executar a tool localmente e responder com `TOOL_CALL_RESULT`. A execução real da tool reaproveita o `get_weather(city)` já existente no backend (issue #5) em vez de mockar o resultado.

- **Issue:** [#33 — `[Back] -A2UI- Wire existing get_weather tool as an AG-UI server-side tool call`](https://github.com/doljak-projects/A2UI_A17_Python/issues/33)

### Passo 3 — [Front] Consumir os eventos do agente com HttpAgent + AgentSubscriber
No Angular, instanciar um `HttpAgent` apontando para o endpoint do agente, montar um `AgentSubscriber` com um handler por tipo de evento, adicionar a mensagem do usuário (`agent.addMessage(...)`) e disparar `agent.runAgent(...)`. Objetivo é apenas logar/exibir os eventos recebidos, para validar o transporte ponta a ponta.

- **Issue:** [#34 — `[Front] -AG-UI- Consume agent events via HttpAgent and AgentSubscriber`](https://github.com/doljak-projects/A2UI_A17_Python/issues/34)

### Passo 4 — [Front] Tool client-side de clima (schema + preparação de renderização)
Definir uma `Tool` do lado do cliente (schema via `zod`, ex.: `condition`, `temperature`, `wind`) que descreve os dados de clima que o **cliente** sabe renderizar, e registrar essa tool na chamada de `runAgent`. Preparar (sem finalizar UI) a estrutura de dados que vai alimentar a exibição do card de clima no `ChatComponent` (issue #25).

- **Issue:** [#35 — `[Front] -A2UI- Define client-side weather Tool schema for chat rendering`](https://github.com/doljak-projects/A2UI_A17_Python/issues/35)

### Passo 5 — [Front] Ciclo de duas runs para tool call client-side
Implementar o fluxo completo de tool call no cliente: 1ª run com `tools: [showWeatherTool]`, inspecionar a resposta em busca de um pedido de tool call, executar a ação local correspondente, montar a mensagem de resultado, adicionar via `agent.addMessage(...)` e disparar a 2ª run. Este passo fecha o ciclo descrito no artigo (server-side vs client-side tool calls) dentro do fluxo de chat do A2UI.

- **Issue:** [#36 — `[Front] -A2UI- Two-run cycle for client-side weather tool call result`](https://github.com/doljak-projects/A2UI_A17_Python/issues/36)

## 4. O que fica para depois

O próprio artigo termina apontando que usar o SDK diretamente gera boilerplate, e que a próxima parte da série mostra como abstrair isso para Angular de forma mais idiomática ("AG-UI End to End: Connecting Server and Client"). Isso deve virar a **Parte 2** deste tutorial, com suas próprias issues, quando este tutorial for continuado.