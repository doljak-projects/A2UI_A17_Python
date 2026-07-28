---
issue: 32
title: "[Back] -AG-UI- Agent skeleton emitting RUN_STARTED/TEXT_MESSAGE/RUN_FINISHED events"
branch: feat/agui-agent-32-skeleton-events
status: closed
last_updated: 07-28-2026
---

# Issue #32 — Agent skeleton emitting RUN_STARTED/TEXT_MESSAGE/RUN_FINISHED events

## Objective
Implement a minimal AG-UI-compliant agent skeleton that emits the core event sequence of a chat turn (`RUN_STARTED` → `TEXT_MESSAGE_START/CONTENT/END` → `RUN_FINISHED`), with no LLM call involved yet — the goal is to validate the AG-UI event format itself, following the tutorial "AG-UI in Practice: The SDK for TypeScript".

## Scope
- Implement an agent base class equivalent to `AbstractAgent`
- Emit `RUN_STARTED` with `threadId`/`runId`
- Emit `TEXT_MESSAGE_START` → one or more `TEXT_MESSAGE_CONTENT` deltas → `TEXT_MESSAGE_END`
- Emit `RUN_FINISHED` and complete the stream
- Reference: `docs/tutorial_A2UI/01-ag-ui-sdk-typescript.md` (Passo 1)

## Decisão de arquitetura: TypeScript (artigo) → Python (este projeto)

O artigo original ("AG-UI in Practice: The SDK for TypeScript") implementa o agente com o SDK `@ag-ui/client` em TypeScript, hospedado num runtime Node. Este projeto não tem nenhum runtime Node no backend — `apps/backend` é 100% Python/FastAPI — e o próprio artigo confirma que o AG-UI **não é amarrado a uma linguagem**: "AG-UI comes not only with a protocol specification but also with SDKs for TypeScript and Python", além de citar implementações comunitárias em Java, C++ e frameworks como Spring AI.

Manter dois runtimes (Node + Python) só para replicar o exemplo literalmente introduziria complexidade sem necessidade real — inclusive porque o AG-UI usa **HTTP + SSE** como transporte (não WebSockets), e o FastAPI já implementa esse padrão manualmente hoje em `app/llm/sse.py` / `app/llm/streaming.py` para o endpoint `/api/chat` existente (protocolo ad-hoc do projeto, anterior ao AG-UI).

**Decisão:** todo trabalho *server-side* do AG-UI (issues `[Back]`) será implementado em **Python**, dentro de `apps/backend`, usando o pacote oficial [`ag-ui-protocol`](https://pypi.org/project/ag-ui-protocol/) (PyPI, MIT, Python ≥3.9) — que fornece `ag_ui.core` (tipos de evento em Pydantic) e `ag_ui.encoder.EventEncoder` (serialização para SSE). A sequência e a semântica dos eventos seguem exatamente o artigo; só a linguagem/forma de produzir o stream muda.

### Tabela de equivalência TS → Python

| Conceito no artigo (TS) | Equivalente em Python (este projeto) |
|---|---|
| `AbstractAgent` (classe base abstrata do SDK, método `run()`) | Classe abstrata própria (`ABC`), método `run(input) -> Iterator[BaseEvent]` — não existe pronta no pacote Python, então é construída neste projeto |
| `Observable<BaseEvent>` (stream reativo do RxJS) | **Generator síncrono** — padrão idiomático Python para produzir um stream de eventos (`yield`), já usado hoje em `app/llm/streaming.py` |
| `observer.next(event)` | `yield event` |
| `observer.complete()` | fim implícito do generator (retorno da função) |
| `EventType`, `BaseEvent`, `RunAgentInput` (`@ag-ui/core`) | `ag_ui.core.EventType` e classes de evento equivalentes (`RunStartedEvent`, `TextMessageStartEvent`, etc.) — vêm prontas do pacote `ag-ui-protocol` |
| Envio via SSE (glue code manual no artigo) | `ag_ui.encoder.EventEncoder` — serializa os eventos Pydantic em linhas `data: ...` de SSE, papel equivalente ao que `app/llm/sse.py` já faz "na mão" para o protocolo ad-hoc atual |
| `FlightWeatherAgent extends AbstractAgent` | Classe concreta própria (ex: `WeatherChatAgent`), implementando a base acima, emitindo `RUN_STARTED` → `TEXT_MESSAGE_START/CONTENT/END` → `RUN_FINISHED` |
| `HttpAgent` + `AgentSubscriber` (lado cliente, Angular) | Fora do escopo desta issue — pertence à issue #34 (`[Front]`), lado do cliente Angular |

Esta decisão vale como padrão para as próximas issues `[Back]` do tutorial (ex: #33): tudo que for lógica de agente/servidor AG-UI é implementado em Python usando essa mesma equivalência, sem introduzir Node no monorepo.

## Status
> Atualizado em: 07-28-2026

- [x] Adicionar `ag-ui-protocol` às dependências do backend (`requirements.txt`)
- [x] Criar classe base abstrata do agente (equivalente a `AbstractAgent`) — `app/agui/agent.py::AGUIAgent`
- [x] Implementar agente concreto emitindo `RUN_STARTED` → `TEXT_MESSAGE_START/CONTENT/END` → `RUN_FINISHED` — `app/agui/agent.py::WeatherChatAgent`
- [x] Testes cobrindo a sequência de eventos emitida — `tests/test_agui_agent.py` (5 testes)
- [x] Rota HTTP de demo para teste funcional ponta a ponta — `GET /api/agui/demo` (`app/api/routes/agui.py`), com `tests/test_agui_endpoint.py` (2 testes)
- Suíte completa do backend: **94 passed**, `ruff check` limpo

## Como testar funcionalmente

Esta issue não tinha, no escopo original, nenhum endpoint HTTP (só validar o formato dos eventos). Para permitir teste funcional ponta a ponta, foi adicionada uma rota de demo:

### Backend

```bash
cd apps/backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Em outro terminal:

```bash
curl -N http://127.0.0.1:8000/api/agui/demo
```

`-N` desabilita o buffer do curl, então os eventos SSE aparecem conforme chegam (embora, sem LLM real, cheguem quase instantaneamente). Saída esperada — a mesma sequência do artigo, em formato AG-UI real:

```
data: {"type":"RUN_STARTED","threadId":"<uuid>","runId":"<uuid>"}

data: {"type":"TEXT_MESSAGE_START","messageId":"1001","role":"assistant"}

data: {"type":"TEXT_MESSAGE_CONTENT","messageId":"1001","delta":"Consultando o clima para São Paulo..."}

data: {"type":"TEXT_MESSAGE_END","messageId":"1001"}

data: {"type":"RUN_FINISHED","threadId":"<uuid>","runId":"<uuid>"}
```

Também é possível abrir `http://127.0.0.1:8000/docs` (Swagger) e testar `GET /api/agui/demo` por lá — o Swagger não renderiza o stream token a token, mas mostra a resposta completa.

Alternativa sem subir servidor, direto em Python (útil para depurar o agente isolado, sem FastAPI):

```python
from ag_ui.core import RunAgentInput
from ag_ui.encoder import EventEncoder
from app.agui.agent import WeatherChatAgent

run_input = RunAgentInput(
    thread_id="thread-demo-1", run_id="run-demo-1",
    state=None, messages=[], tools=[], context=[], forwarded_props={},
)
encoder = EventEncoder()
for event in WeatherChatAgent().run(run_input):
    print(encoder.encode(event), end="")
```

### Frontend

Ainda **não há nada no frontend** para esta issue — o consumo do lado cliente (`HttpAgent` + `AgentSubscriber`) é escopo da issue #34 (`[Front] -AG-UI- Consume agent events via HttpAgent and AgentSubscriber`). Até lá, o teste funcional do lado do agente é só via backend (curl/Swagger/script Python acima).

Quando a #34 for implementada, o teste funcional de frontend passa a ser: rodar `npm run fe:start`, abrir a tela que consome `/api/agui/demo` (ou o endpoint real do chat, quando migrado) e verificar no DevTools (Network → EventStream) que os eventos chegam na mesma sequência mostrada acima, e que o `AgentSubscriber` do Angular loga/renderiza cada um.

## Notes
- Sem chamada real ao LLM nesta issue — só validar o formato/sequência dos eventos AG-UI, como no artigo original.
- `RunAgentInput` (do pacote `ag-ui-protocol`) exige todos os campos (`state`, `messages`, `tools`, `context`, `forwarded_props`) — não há defaults, diferente do `RunAgentInput` do artigo em TS onde só `runId`/`threadId` aparecem no exemplo.
- `EventEncoder().encode(event)` já serializa os eventos Pydantic para o formato SSE (`data: {...}\n\n`) com campos em camelCase (`threadId`, `runId`) — equivalente ao `format_sse()` que o projeto já tem em `app/llm/sse.py`. A rota `/api/agui/demo` usa o encoder diretamente, então o SSE gerado já é 100% AG-UI compliant (não passa pelo `format_sse()` ad-hoc do protocolo antigo).
- A rota de demo (`GET /api/agui/demo`) é só para validação manual desta issue — não é a rota final de produção; quando o agente ganhar lógica real (LLM, tool calls), a integração deve substituir ou conviver com `/api/chat` de forma deliberada, não por acidente.
- A tool call server-side (clima) fica para a issue #33, que reaproveita esta base.
