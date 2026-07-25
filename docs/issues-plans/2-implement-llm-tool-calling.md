---
issue: 2
title: "BE: Implementar tool calling / function calling com o LLM"
branch: feat/2-tool-calling-implement-llm-tool-calling
status: closed
last_updated: 07-25-2026
---

# Issue #2 — BE: Implementar tool calling / function calling com o LLM

## Status
Feita — mecânica de tool calling implementada sobre o `ToolRegistry` da #6, com testes.

## O que foi feito
- Tipos internos agnósticos de provedor em `app/llm/types.py`: `Message`, `ToolCall`, `ToolResult` e `LLMResponse` (com `requires_tool_execution`).
- `app/llm/providers.py`: montagem do payload de tools e de mensagens para **OpenAI** (`type: function` / `tool_calls`) e **Anthropic** (`input_schema` / `tool_use` / `tool_result`), mais o parsing normalizado das respostas dos dois formatos.
- `app/llm/client.py`: protocolo `LLMClient` e `HttpLLMClient` (httpx) para os dois provedores, montando headers, `model`, `temperature`, `max_tokens` e `tools` a partir do `Settings` da #1. Prompt de sistema é extraído para o campo `system` no caso da Anthropic.
- `app/llm/tool_calling.py`: loop `run_tool_calling()` que envia a conversa com as tools disponíveis, detecta o pedido de execução, roda as tools via `registry.execute_tool()` e devolve os resultados na rodada seguinte até o LLM responder sem tools. Inclui limite de rodadas (`MaxToolRoundsExceededError`) e captura de erro de tool como `ToolResult(is_error=True)`.
- `httpx` promovido para `requirements.txt` (passou a ser dependência de runtime).
- Testes: `tests/test_llm_providers.py` (payload e parsing dos dois provedores) e `tests/test_tool_calling.py` (ciclo completo com a tool `echo`, propagação do resultado para a rodada seguinte, erro de tool e limite de rodadas).

## Como rastrear
- Branch: `feat/2-tool-calling-implement-llm-tool-calling`
- Worktree: `2-worktree-tool-calling`
- Arquivos principais: `apps/backend/app/llm/` (`types.py`, `providers.py`, `client.py`, `tool_calling.py`), `apps/backend/tests/test_llm_providers.py`, `apps/backend/tests/test_tool_calling.py`

## Notes
- Critério de conclusão atendido: o LLM invoca a tool de teste `echo` e o backend retorna a resposta final — validado com um cliente falso, sem depender de chave real. A suíte tem 22 testes passando.
- Erros de tool não interrompem o loop: viram `ToolResult(is_error=True)` para o LLM poder se corrigir.
- O `HttpLLMClient` é não-streaming por design; o streaming entra na issue #3.
- Commit/push/PR permanecem manuais.
