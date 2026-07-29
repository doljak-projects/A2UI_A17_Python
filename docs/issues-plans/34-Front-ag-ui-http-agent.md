---
issue: 34
title: "[Front] -AG-UI- Consume agent events via HttpAgent and AgentSubscriber"
branch: feat/agui-http-agent-34-consume-events
status: in-progress
last_updated: 07-29-2026
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
> Atualizado em: 07-29-2026

- [x] Passo 1 — SDK instalado (`@ag-ui/client`, `@ag-ui/core`); confirmado via leitura do build (`node_modules/@ag-ui/client/dist/index.mjs`) que `HttpAgent.requestInit()` é `protected` e sobrescrevível, e que o default é sempre `POST` com o `RunAgentInput` inteiro como corpo — nossas rotas são `GET` sem corpo, então a solução é uma subclasse local sobrescrevendo só esse método (sem tocar no backend)
- [ ] Passo 2 — Criar o serviço/wrapper Angular isolado para o agente AG-UI (nome do arquivo/classe a definir com o usuário)
- [ ] Passo 3 — Construir o `AgentSubscriber` com os handlers de texto (e decidir se cobre também os de tool call, já emitidos por `/agui/weather-tool-demo`)
- [ ] Passo 4 — Disparar `agent.addMessage(...)` + `agent.runAgent(...)` a partir de um ponto de entrada simples de teste
- [ ] Passo 5 — Testes (padrão de 3 camadas já usado no projeto: parser puro / service com fetch mockado / componente com stub)
- [ ] Passo 6 — Validação funcional manual (backend + frontend rodando, DevTools → Network → EventStream)

## Notes
- `ChatService`/`ChatComponent` existentes **não são tocados** nesta issue — ficam no protocolo SSE ad-hoc do projeto. O AG-UI ganha arquivos próprios e isolados.
