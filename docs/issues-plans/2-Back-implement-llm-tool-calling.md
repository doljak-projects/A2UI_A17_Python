---
issue: 2
title: "BE: Implementar tool calling / function calling com o LLM"
branch: feat/2-tool-calling-implement-llm-tool-calling
status: closed
last_updated: 07-25-2026
---

# Issue #2 — Implementar tool calling / function calling com o LLM

## Status
Feita — mecânica de tool calling implementada sobre o `ToolRegistry` da #6, com testes.

## O que foi feito
- Tipos internos agnósticos de provedor em `app/llm/types.py`: `Message`, `ToolCall`, `ToolResult` e `LLMResponse` (com `requires_tool_execution`).
- `app/llm/providers.py`: montagem do payload de tools e de mensagens para **OpenAI** e **Anthropic**, mais parsing normalizado das respostas.
- `app/llm/client.py`: protocolo `LLMClient` e `HttpLLMClient` (httpx) para os dois provedores.
- `app/llm/tool_calling.py`: loop `run_tool_calling()` com limite de rodadas e captura de erro de tool como `ToolResult(is_error=True)`.
- `httpx` promovido para `requirements.txt`.
- Testes: `tests/test_llm_providers.py` e `tests/test_tool_calling.py`.

## Como rastrear
- Branch: `feat/2-tool-calling-implement-llm-tool-calling`
- Worktree: `2-worktree-tool-calling`
- Arquivos principais: `apps/backend/app/llm/`, `apps/backend/tests/test_llm_providers.py`, `apps/backend/tests/test_tool_calling.py`

## Notes
- O `HttpLLMClient` é não-streaming por design; o streaming entra na issue #3.
- Erros de tool não interrompem o loop: viram `ToolResult(is_error=True)` para o LLM poder se corrigir.
