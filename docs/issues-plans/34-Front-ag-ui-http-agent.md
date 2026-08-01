---
issue: 34
title: "[Front] -AG-UI- Consume agent events via HttpAgent and AgentSubscriber"
branch: feat/agui-http-agent-34-consume-events
status: closed
last_updated: 08-01-2026
---

# Issue #34 — Consume agent events via HttpAgent and AgentSubscriber

## Objective
In Angular, instantiate an `HttpAgent` (from `@ag-ui/client`) pointing at the agent endpoint, build an `AgentSubscriber` with one handler per AG-UI event type, add the user message and trigger `agent.runAgent(...)`. Goal is to validate the end-to-end transport by logging/displaying received events.

## Scope
- Instantiate `HttpAgent` with the agent URL and a `threadId`
- Build an `AgentSubscriber` implementing handlers for `onRunStartedEvent`, `onTextMessageStartEvent`, `onTextMessageContentEvent`, `onTextMessageEndEvent`, `onRunFinishedEvent`
- Call `agent.addMessage(userMessage)` followed by `await agent.runAgent(...)`
- Log each received event to validate the stream end to end
- Reference: `docs/tutorial_A2UI/01-ag-ui-sdk-typescript.md` (Passo 3)

## Diagrama
Ver [`docs/diagrams/34-front-agui-http-agent.md`](../diagrams/34-front-agui-http-agent.md) — sequência completa da chamada, onde cada arquivo mora, e o ajuste de `requestInit()` (GET vs POST).

## Modo de trabalho desta issue
A pedido do usuário, esta issue (e as próximas do lado frontend) segue um formato **mentorado**: antes de cada trecho de código, o conceito/decisão é explicado, o usuário confirma entendimento, só então o código é escrito — passos pequenos, um de cada vez.

## Status
> Atualizado em: 08-01-2026

- [x] Passo 1 — SDK instalado (`@ag-ui/client`, `@ag-ui/core`); confirmado via leitura do build (`node_modules/@ag-ui/client/dist/index.mjs`) que `HttpAgent.requestInit()` é `protected` e sobrescrevível, e que o default é sempre `POST` com o `RunAgentInput` inteiro como corpo — nossas rotas são `GET` sem corpo, então a solução é uma subclasse local sobrescrevendo só esse método (sem tocar no backend)
- [x] Passo 2 — Criado `core/services/agui-get-http-agent.ts` (`AguiGetHttpAgent extends HttpAgent`, override de `requestInit()` para `GET` sem body) e `core/services/agui-agent.service.ts` (`AguiAgentService`, `providedIn: 'root'`, getter `getAgent()`, aponta para `GET /api/agui/weather-tool-demo`). Só o getter por enquanto — `addMessage`/`runAgent` ficam para o Passo 4.
- [x] Passo 3 — Criado `core/services/agui-log-subscriber.ts` (`aguiLogSubscriber`) com os 5 handlers do escopo da issue (`onRunStartedEvent`, `onTextMessageStartEvent`, `onTextMessageContentEvent`, `onTextMessageEndEvent`, `onRunFinishedEvent`, todos com `console.log`); tool call ficou fora, por não constar no escopo — é assunto de #35/#36. Registrado no `AguiAgentService` via `agent.subscribe(...)` no construtor.
- [x] Passo 4 — Criado `pages/agui-test/` (`AguiTestComponent`, standalone, sem Signals no subscriber — só o `status` local do componente usa `signal`), com botão que dispara `addMessage` + `runAgent`. Rota isolada `/agui-test` adicionada em `app.routes.ts`, sem tocar em `ChatComponent`/`ChatService`.
- [x] Passo 5 — Testes nas 3 camadas: `agui-get-http-agent.spec.ts` (unidade pura do override de `requestInit`), `agui-agent.service.spec.ts` (TestBed, verifica URL/thread e registro do `aguiLogSubscriber`), `agui-test.component.spec.ts` (componente com `AguiAgentServiceStub`, cobre sucesso e falha do `runAgent`). 8/8 verdes. Suíte completa: 26/29 — as 3 falhas são pré-existentes em `chat.component.spec.ts`, não relacionadas a esta issue (falham isoladamente, sem nenhum arquivo AG-UI carregado).
- [x] Passo 6 — Validação funcional manual feita: backend (`uvicorn`) + frontend (`ng serve`) rodando localmente, `.env` copiado da worktree `main` (já com `WEATHER_API_KEY` configurada). `curl` em `GET /api/agui/weather-tool-demo` confirmou a sequência completa de eventos (`RUN_STARTED` → `TOOL_CALL_*` → `RUN_FINISHED`) com dado real da WeatherAPI. No navegador, `/agui-test` → botão "Rodar agente" → eventos logados no console via `aguiLogSubscriber`, confirmado pelo usuário.

## Decisões de implementação

> Racional por trás das escolhas de cada passo — para quem (humano ou IA) retomar este trabalho sem o contexto da conversa original.

**Por que uma subclasse de `HttpAgent` (Passo 1/2)**
Lendo `node_modules/@ag-ui/client/dist/index.mjs`, o `requestInit()` default do SDK é:
```js
requestInit(input) {
  return {
    method: 'POST',
    headers: { ...this.headers, 'Content-Type': 'application/json', Accept: 'text/event-stream' },
    body: JSON.stringify(input),
    signal: this.abortController.signal,
  };
}
```
Sempre `POST` com o `RunAgentInput` inteiro serializado no corpo. As rotas AG-UI do backend (`GET /api/agui/demo`, `GET /api/agui/weather-tool-demo`) são `GET` sem corpo. Como o método é `protected` e documentado como "Override this to customize the request", a solução é uma subclasse local (`AguiGetHttpAgent`) que sobrescreve só esse método — devolve `GET`, sem `body`, mantendo `headers`/`signal` originais. Nenhuma mudança no backend foi necessária.

**Por que `AguiAgentService` injetável em vez de instanciar o agente direto no componente (Passo 2)**
`providedIn: 'root'` garante uma única instância do Angular DI compartilhada entre qualquer componente que injete o serviço — ou seja, todos falam com o mesmo `AguiGetHttpAgent`/`threadId`, em vez de cada consumidor criar seu próprio agente e fragmentar a thread. Foi decisão explícita do usuário priorizar reaproveitamento sobre a alternativa (a própria subclasse de `HttpAgent` como `@Injectable`).

**Por que `agui-log-subscriber.ts` em arquivo separado, não dentro do service (Passo 3)**
Responsabilidade única: `AguiAgentService` cuida do ciclo de vida do agente (criar, configurar URL/thread, registrar subscribers); montar os handlers de log é uma responsabilidade distinta (observar/logar eventos). Por indicação do usuário, esses handlers não usam Signals — ficam desacoplados de primitivas de reatividade do Angular, facilitando uma migração futura (ex: trocar por outro mecanismo de state/observação sem reescrever o service).

**Por que só os 5 handlers de texto/execução, sem tool call (Passo 3)**
O escopo literal da issue #34 lista `onRunStartedEvent`, `onTextMessageStartEvent`, `onTextMessageContentEvent`, `onTextMessageEndEvent`, `onRunFinishedEvent` — nenhum handler de tool call, mesmo apontando para `weather-tool-demo` (que emite `TOOL_CALL_*`). As issues #35/#36 tratam de tool **client-side**, não da leitura de tool call server-side no `AgentSubscriber`; cobrir isso aqui seria extrapolar o escopo combinado.

**Compatibilidade com o tutorial (`docs/tutorial_A2UI/01-ag-ui-sdk-typescript.md`)**
O tutorial descreve o Passo 3 em nível conceitual (instanciar `HttpAgent`, montar `AgentSubscriber`, disparar `addMessage`/`runAgent`) sem prescrever nome de arquivo ou estrutura de classes — a sintaxe do SDK é citada "exatamente como no artigo", só o conteúdo de exemplo é adaptado. A divisão em `agui-get-http-agent.ts` + `agui-agent.service.ts` + `agui-log-subscriber.ts` é uma decisão de organização própria do projeto, sem conflitar com o tutorial.

**Ponto de entrada isolado (Passo 4)**
`AguiTestComponent`/rota `/agui-test` foram criados para não tocar em `ChatComponent`/`ChatService` (que seguem no protocolo SSE ad-hoc do projeto). O `status` local do componente usa `signal` normalmente — a restrição de não usar Signals vale só para o `AgentSubscriber`, não para o estado de UI do componente em si.

## Notes
- `ChatService`/`ChatComponent` existentes **não são tocados** nesta issue — ficam no protocolo SSE ad-hoc do projeto. O AG-UI ganha arquivos próprios e isolados.
