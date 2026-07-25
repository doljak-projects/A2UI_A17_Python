---
issue: 24
title: "FE: ChatService — consumir POST /api/chat via SSE (fetch streaming)"
branch: feat/24-chat-service-consume-post-api-chat-via-sse
status: closed
last_updated: 07-25-2026
---

# Issue #24 — ChatService com fetch + SSE

## Status
Feita — serviço Angular consome `POST /api/chat` via `fetch` + `ReadableStream`, com parser SSE e testes unitários.

## O que foi feito
- `src/environments/environment.ts`: `apiBaseUrl` apontando para `http://localhost:8000/api` (mesma origem do backend local).
- `app/core/models/chat.models.ts`: tipos `ChatMessage` e union `ChatEvent` alinhados ao contrato real do backend (`delta`, `tool_call`, `tool_result`, `done`, `error`) — a issue citava `text_delta`/`message_stop`, mas o backend usa outros nomes.
- `app/core/services/sse-parser.ts`: parser puro de linhas SSE (`feedSseParser`) e mapeamento `toChatEvent`, testável sem Angular.
- `app/core/services/chat.service.ts`: `ChatService.send(messages)` retorna `Observable<ChatEvent>` usando `fetch` com `Accept: text/event-stream`, lê o corpo com `getReader()` e emite eventos conforme chegam; cancelamento via `AbortController` no teardown do Observable.
- `sse-parser.spec.ts` e `chat.service.spec.ts`: 8 testes (parser + stream mockado, erro HTTP, evento `error` do SSE).

## Como rastrear
- Branch: `feat/24-chat-service-consume-post-api-chat-via-sse`
- Worktree: `24-worktree-chat-service`
- Arquivos principais: `apps/frontend/src/app/core/services/chat.service.ts`, `apps/frontend/src/app/core/services/sse-parser.ts`, `apps/frontend/src/app/core/models/chat.models.ts`

## Notes
- O `HttpClient` do Angular não suporta streaming incremental do corpo — por isso `fetch` nativo.
- A issue #25 (`ChatComponent`) deve consumir `delta` para acumular texto e fechar no `done`; `tool_call`/`tool_result` podem ser ignorados na primeira versão da UI ou exibidos como indicador.
- Validação: 8 testes novos passando + `ng build` sem erros.
