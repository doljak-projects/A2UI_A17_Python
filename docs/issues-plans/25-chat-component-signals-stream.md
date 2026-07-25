---
issue: 25
title: "FE: ChatComponent — layout, estado com Signals e renderização de stream"
branch: feat/25-chat-component-layout-signals-stream-rendering
status: closed
last_updated: 07-25-2026
---

# Issue #25 — ChatComponent com Signals e streaming

## Status
Feita — UI de chat com bolhas, estado em Signals e acumulação incremental de `delta` do `ChatService`.

## O que foi feito
- `app/pages/chat/chat.component.ts`: estado com `messages`, `isStreaming` e `error` como `WritableSignal`; ao enviar, acrescenta mensagem do usuário + placeholder do assistente, chama `ChatService.send()` e concatena eventos `delta` na última bolha.
- Template: lista rolável com bolhas user/assistant, spinner enquanto o assistente ainda não emitiu texto, formulário com textarea + botão enviar desabilitado durante o stream.
- `chat.component.scss`: layout flex em coluna, altura quase fullscreen, bolhas alinhadas à direita (user) e esquerda (assistant).
- `chat.component.spec.ts`: 6 testes com `ChatService` stubado (acumulação de deltas, mensagem vazia, bloqueio durante stream aberto, erros SSE e de rede).

## Como rastrear
- Branch: `feat/25-chat-component-layout-signals-stream-rendering`
- Worktree: `25-worktree-chat-component`
- Arquivos principais: `apps/frontend/src/app/pages/chat/chat.component.ts`, `chat.component.html`, `chat.component.scss`, `chat.component.spec.ts`

## Notes
- Eventos `tool_call`/`tool_result` são ignorados na UI por enquanto — só `delta` e `error` alteram o estado visível; a #26 adiciona a rota.
- Auto-scroll via `ViewChild` + `ngAfterViewChecked` com flag `shouldScroll`, para não forçar scroll em todo change detection.
- O histórico enviado ao backend exclui o placeholder vazio do assistente (`slice(0, -1)`).
- Validação: 6 testes novos passando + `ng build` sem erros.
