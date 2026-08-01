---
tutorial_part: 2
source_title: "Agentic UI with Angular, CopilotKit, and AG-UI"
source_url: https://www.angulararchitects.io/en/blog/implementing-ag-ui-with-angular/
source_series: "Agentic UI with Angular (Angular Architects) — artigo 4 de 10"
status: draft
last_updated: 2026-08-01
---

# Tutorial A2UI — Parte 2: CopilotKit + AG-UI no Angular

> Documento agnóstico: escrito para ser lido tanto por humanos quanto por outras IAs que venham a continuar este trabalho no projeto A2UI. Cada passo abaixo tem uma issue equivalente no GitHub.

## 1. Resumo geral

A Parte 1 deste tutorial (issues #32–#36) usou o SDK AG-UI **na mão**: uma subclasse de `HttpAgent` sobrescrevendo `requestInit()`, um `AgentSubscriber` manual pra logar eventos, e um ciclo de duas `runAgent()` calls montado à mão pra resolver uma tool call client-side. Funcionou, mas o próprio artigo da Parte 1 já apontava que isso gera bastante boilerplate.

Este artigo (4º de uma série de 10 chamada "Agentic UI with Angular", mesmo autor) mostra como o **CopilotKit** (`@copilotkit/angular`) abstrai esse boilerplate: um *agent store* baseado em Signals, ferramentas client-side declaradas com `createFrontendTool` (executadas automaticamente pelo SDK, sem gerenciar runs manualmente), e widgets — componentes Angular anexados a uma tool call, renderizados direto no histórico do chat via `<copilot-render-tool-calls>`.

O artigo original usa um domínio de reserva de voos ("ticketing") com um backend em **Mastra** (framework de agentes em TypeScript/Node). O A2UI **não usa Mastra** — o backend é Python/FastAPI com o pacote `ag-ui-protocol` (decisão já tomada na Parte 1, doc da issue #32). Isso não é um problema: o CopilotKit consome qualquer backend compatível com o protocolo AG-UI através do mesmo `HttpAgent` do `@ag-ui/client` — só a implementação do agente do lado do servidor muda, não o protocolo. Este tutorial adapta os exemplos do artigo (voos, `ticketingAgent`) para o domínio já estabelecido do projeto (clima, `get_weather`, `show_weather`).

### Por que isso importa para o A2UI

As issues #34–#36 provaram o protocolo AG-UI funcionando ponta a ponta, mas com um limite conhecido: o transporte de demo usava `GET` sem corpo, então a 2ª run de uma tool call client-side nunca chegava a informar o backend sobre o resultado (ver `## Decisão de arquitetura` no doc da issue #36). O CopilotKit usa `POST` com corpo por padrão — adotar essa Parte 2 é a oportunidade natural de resolver essa limitação de vez (issue #45), além de trocar o código manual das issues #34–#36 pela abordagem mais idiomática que o próprio SDK oferece.

## 2. Conceitos-chave do artigo

| Conceito | Lado | O que é |
|---|---|---|
| `provideCopilotKit(config)` | Cliente | Provider de aplicação que inicializa o CopilotKit; `defaultToolRendering: true` ativa uma renderização padrão pra tools sem componente |
| Agent store (`initAgentStore` + `injectAgentStore`) | Cliente | Padrão de registro de agente em runtime (bom pra áreas lazy-loaded); expõe `messages()`/`isRunning()` como Signals |
| `AppHttpAgent` | Cliente | Subclasse de `HttpAgent` (`@ag-ui/client`) usada pelo agent store — no artigo, adiciona suporte a `useServerMemory` |
| `createFrontendTool` | Cliente | Helper que infere o tipo dos parâmetros a partir do schema Zod; define `name`/`description`/`parameters`/`handler` (e opcionalmente `component`) |
| `registerFrontendTool` | Cliente | Registra a tool com binding ao `agentId`; preserva o contexto de injeção do Angular (`inject()` funciona dentro do `handler`) |
| Widget (`component` + `ToolRenderer<T>`) | Cliente | Não é um conceito à parte — é uma frontend tool com um componente Angular anexado, renderizado no histórico do chat |
| `<copilot-render-tool-calls>` | Cliente | Componente do CopilotKit que procura o widget registrado pra cada tool call e o renderiza com os parâmetros já tipados |
| `sendMessage` (helper) | Cliente | `agent.addMessage(...)` + `copilotKit.core.runAgent({ agent })` — dispara uma run a partir do input do usuário |

## 3. Passos didáticos e issues equivalentes

Mesma convenção da Parte 1:
- **`-AG-UI-`** no título → mecânica do protocolo/SDK em si.
- **`-A2UI-`** no título → integração específica no projeto A2UI (reaproveitando `get_weather`, o domínio de clima, etc.).
- Prefixo `[Back]` ou `[Front]` indica se o trabalho é no `apps/backend` ou `apps/frontend`.

### Passo 1 — [Back] Endpoint AG-UI que aceita POST real e resolve o ciclo de tool call
Criar um endpoint `POST /api/agui/weather-tool-agent-demo` que recebe um `RunAgentInput` de verdade (com `messages`) e reage de acordo: se ainda não há uma `ToolMessage` respondendo `show_weather`, emite a tool call pendente (igual à issue #36); se já há, responde com uma mensagem de texto confirmando os dados recebidos. Resolve, pra valer, a limitação de transporte GET-only documentada na issue #36.

- **Issue:** [#45 — `[Back] -AG-UI- Accept a real RunAgentInput via POST for a resumable weather tool-call agent`](https://github.com/doljak-projects/A2UI_A17_Python/issues/45)

### Passo 2 — [Front] Instalar e configurar o CopilotKit
Adicionar `@copilotkit/angular` ao workspace do frontend e registrar `provideCopilotKit({ defaultToolRendering: true })` em `app.config.ts`. Sem nenhum agente ainda — só a base do provider.

- **Issue:** [#46 — `[Front] -AG-UI- Install and configure CopilotKit for Angular`](https://github.com/doljak-projects/A2UI_A17_Python/issues/46)

### Passo 3 — [Front] Agent store: AppHttpAgent + initAgentStore + injectAgentStore
Implementar `AppHttpAgent` (subclasse de `HttpAgent`), o helper `initAgentStore` (registra o agente no runtime do CopilotKit) e `injectWeatherAgentStore()` (expõe `messages()`/`isRunning()` como Signals), apontando pro endpoint novo da issue #45.

- **Issue:** [#47 — `[Front] -AG-UI- Agent store: AppHttpAgent, initAgentStore and injectAgentStore`](https://github.com/doljak-projects/A2UI_A17_Python/issues/47)

### Passo 4 — [Front] Tool de clima via createFrontendTool
Reimplementar a tool client-side de clima (issues #35–#36) com `createFrontendTool`, cujo `handler` o CopilotKit executa sozinho dentro de `runAgent` — sem precisar do `AgentSubscriber` manual nem do ciclo de duas runs montado à mão na issue #36.

- **Issue:** [#48 — `[Front] -A2UI- Weather frontend tool via createFrontendTool`](https://github.com/doljak-projects/A2UI_A17_Python/issues/48)

### Passo 5 — [Front] Widget de clima via copilot-render-tool-calls
Anexar um componente Angular (`WeatherWidget`, implementando `ToolRenderer<WeatherToolResult>`) à tool de clima, renderizado como card interativo direto no histórico do chat via `<copilot-render-tool-calls>`.

- **Issue:** [#49 — `[Front] -A2UI- Weather widget rendered via copilot-render-tool-calls`](https://github.com/doljak-projects/A2UI_A17_Python/issues/49)

### Passo 6 — [Front] UI de chat sidecar ligada ao agent store
Montar uma UI de chat de demonstração isolada (mesmo princípio de isolamento do `/agui-test` das issues #34–#36 — sem tocar em `ChatComponent`/`ChatService`), usando `sendMessage()` e renderizando `messages()`/`isRunning()`.

- **Issue:** [#50 — `[Front] -A2UI- Sidecar chat UI wired to the CopilotKit agent store`](https://github.com/doljak-projects/A2UI_A17_Python/issues/50)

## 4. O que fica para depois

O artigo 5 da série ("A2UI: How AI Generates Dynamic UIs at Runtime") introduz o conceito de A2UI de verdade — o modelo compõe UI em runtime a partir de primitivos (layout, display, input), sem precisar de deploy de novo código de frontend. Esse é o próximo tema natural a documentar como **Parte 3** deste tutorial, quando chegar a vez.
