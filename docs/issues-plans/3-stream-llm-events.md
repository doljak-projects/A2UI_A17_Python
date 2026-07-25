---
issue: 3
title: "BE: Tratar streaming de eventos LLM no backend"
branch: feat/3-chat-streaming-stream-llm-events
status: closed
last_updated: 07-25-2026
---

# Issue #3 — Streaming de eventos do LLM via SSE

## Status
Feita — endpoint `POST /api/chat` em SSE, com tool use no meio do stream; validado com servidor real.

## O que foi feito
- `app/llm/sse.py`: `iter_sse_json` extrai os payloads das linhas `data:` (serve para OpenAI e Anthropic, ignora `event:`/comentários e encerra no `[DONE]`) e `format_sse` serializa um evento no formato SSE.
- `app/llm/client.py`: novo protocolo `StreamingLLMClient` e método `HttpLLMClient.stream()`, que reaproveita `_headers`/`_body` acrescentando `stream: True` e devolve os chunks já desserializados. Em resposta de erro o corpo é lido antes do `raise_for_status` para a mensagem do provedor não se perder.
- `app/llm/streaming.py`: acumuladores por provedor (`OpenAIStreamAccumulator`, `AnthropicStreamAccumulator`) que remontam texto e tool calls fatiadas, e `stream_tool_calling`, versão em streaming de `run_tool_calling` que emite `StreamEvent` (`delta`, `tool_call`, `tool_result`, `done`).
- `app/api/routes/chat.py`: endpoint `POST /api/chat` devolvendo `StreamingResponse` com `media_type="text/event-stream"` e headers anti-buffer; falhas viram evento `error` porque a resposta já saiu como 200.
- `app/schemas/chat.py`: `ChatRequest`/`ChatMessage` — o histórico inteiro vem do cliente, o backend não guarda estado.
- `tests/test_llm_streaming.py` e `tests/test_chat_endpoint.py`: 17 testes cobrindo parsing de SSE, remontagem de tool calls fragmentadas e paralelas, os dois provedores, ordem dos eventos, realimentação dos resultados na rodada seguinte, erro de tool, limite de rodadas e o contrato HTTP do endpoint.

## Como rastrear
- Branch: `feat/3-chat-streaming-stream-llm-events`
- Worktree: `3-worktree-chat-streaming`
- Arquivos principais: `apps/backend/app/llm/streaming.py`, `apps/backend/app/llm/sse.py`, `apps/backend/app/api/routes/chat.py`, `apps/backend/app/schemas/chat.py`

## Notes
- **Uma conexão SSE, N requisições ao LLM.** Cada rodada de tool calling abre um request novo ao provedor, mas o cliente enxerga um fluxo contínuo. É o que permite emitir `tool_call`/`tool_result` no meio dos deltas sem quebrar o stream.
- **Tool call chega fatiada.** A OpenAI manda `function.arguments` em pedaços de JSON (`{"ci`, `ty": "S`, ...) que só podem ser desserializados depois do `finish_reason: tool_calls`; por isso o `_ToolCallDraft` acumula por `index` — o índice também é o que mantém tool calls paralelas separadas.
- **O `EventSource` do browser só faz GET.** Como o endpoint é POST (precisa do histórico no corpo), o frontend terá que consumir com `fetch()` + `ReadableStream`, não com `EventSource` nem com o `HttpClient` padrão do Angular.
- Header `X-Accel-Buffering: no` incluído de propósito: sem ele um nginx na frente segura os deltas e entrega tudo de uma vez, quebrando o critério da issue.
- A rota é `def` (síncrona) porque o `httpx.Client` é síncrono; o Starlette roda o gerador em threadpool. Se um dia o cliente virar `httpx.AsyncClient`, a rota deve virar `async def`.
- Validação: 57 testes passando + `curl`/cliente real medindo os tempos — `tool_call` em 0,72s, `tool_result` em 1,11s e 21 deltas entre 1,72s e 1,95s, ou seja, sem buffer acumulado.
