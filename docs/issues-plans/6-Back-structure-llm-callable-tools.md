---
issue: 6
title: "BE: Estruturar camada de tools chamáveis pelo LLM"
branch: feat/6-tool-registry-structure-llm-callable-tools
status: closed
last_updated: 07-25-2026
---

# Issue #6 — BE: Estruturar camada de tools chamáveis pelo LLM

## Status
Feita — infraestrutura de tools (contrato + registry + dispatcher) implementada e testada.

## O que foi feito
- Contrato de tool em `app/tools/base.py`: classe base `Tool` com `name`, `description`, `input_schema` (JSON Schema) e `execute(arguments) -> output`, além de `schema()` para o payload do LLM.
- `ToolRegistry` em `app/tools/registry.py`: `register`, `get`, `list_tools`, `get_tools_schema()` e `execute_tool(name, arguments)`; erros dedicados `ToolNotFoundError` e `ToolAlreadyRegisteredError`.
- Funções de conveniência no registry padrão: `get_tools_schema()` e `execute_tool()`.
- Tool de exemplo `echo` em `app/tools/examples.py`, registrada de forma idempotente via `register_builtin_tools()`.
- Registro automático das tools embutidas ao importar `app.tools` (`__init__.py`).
- Testes em `tests/test_tools.py`: registro/execução, formato de `get_tools_schema`, duplicidade, tool inexistente e echo no registry padrão.

## Como rastrear
- Branch: `feat/6-tool-registry-structure-llm-callable-tools`
- Worktree: `6-worktree-tool-registry`
- Arquivos principais: `apps/backend/app/tools/base.py`, `apps/backend/app/tools/registry.py`, `apps/backend/app/tools/examples.py`, `apps/backend/app/tools/__init__.py`, `apps/backend/tests/test_tools.py`

## Notes
- Critério de conclusão atendido: registry com a tool `echo` registrada, descoberta (`get_tools_schema`) e executada via `execute_tool()` — 9 testes passando.
- `execute_tool(name, arguments)` recebe os argumentos já desserializados (dict), pronto para o dispatcher usado pelo tool calling (issue #2).
