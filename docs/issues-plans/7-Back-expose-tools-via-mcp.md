---
issue: 7
title: "BE: Expor tools via MCP Server no FastAPI"
branch: feat/7-mcp-server-expose-tools-via-mcp
status: closed
last_updated: 07-25-2026
---

# Issue #7 — Expor as tools do registry via MCP Server

## Status
Feita — servidor MCP espelhando o `ToolRegistry`, montado na própria app FastAPI; validado com cliente MCP externo.

## O que foi feito
- `app/mcp/server.py`: `build_mcp_server(registry=None)` monta o servidor MCP lendo o `ToolRegistry` — as tools não são redeclaradas. O handler de `tools/list` consulta o registry a cada chamada, então tool registrada depois do boot aparece sozinha. O `call_tool` delega para `registry.execute_tool` dentro de `anyio.to_thread.run_sync`, porque `Tool.execute` é síncrono e faz I/O de rede.
- `app/mcp/server.py` (transporte): `build_session_manager()` cria o `StreamableHTTPSessionManager` e `add_mcp_route()` publica o endpoint em `/mcp`.
- `app/main.py`: `create_app()` ganhou `lifespan` que roda o session manager durante toda a vida da app, e `expose_headers=["mcp-session-id"]` no CORS para o cliente conseguir ler o id de sessão.
- `requirements.txt`: `mcp>=1.28,<1.29` e um pino explícito de `starlette>=0.48,<0.51` (ver Notes).
- `docs/mcp.md` + seção no `README.md` da raiz e no `apps/backend/README.md`: endpoint, configuração de cliente para Cursor e Claude Desktop, script de teste e notas de implementação.
- `tests/test_mcp_server.py`: 10 testes usando o transporte **in-memory do próprio SDK** (`create_connected_server_and_client_session`) em vez de mocks, então o caminho exercitado é o protocolo real — listagem, registro dinâmico, invocação, resultado não-dict, tool inexistente, argumentos inválidos, exceção na tool, tools embutidas, listagem sem `WEATHER_API_KEY`, e o endpoint HTTP coexistindo com a API REST.

## Como rastrear
- Branch: `feat/7-mcp-server-expose-tools-via-mcp`
- Worktree: `7-worktree-mcp-server`
- Arquivos principais: `apps/backend/app/mcp/server.py`, `apps/backend/app/main.py`, `apps/backend/tests/test_mcp_server.py`, `docs/mcp.md`

## Notes
- **O session manager precisa rodar no lifespan.** Sem o `run()` ativo, a primeira requisição em `/mcp` estoura com *"Task group is not initialized"*. A instância também é de uso único: por isso é criada dentro de `create_app()`, e não em escopo de módulo.
- **A rota usa `Route`, não `app.mount()`.** Um `Mount("/mcp")` só atenderia `/mcp/` e devolveria 307 para clientes que falam com `/mcp` — que é o que todos fazem.
- **Pino de `starlette` foi necessário**: no Python 3.14, o `mcp` exige `>=0.48` e o `fastapi` aceita `<0.51`; sem fixar a interseção o resolvedor escolhe uma versão que quebra um dos dois.
- Erros viram `CallToolResult` com `isError=true` (tool inexistente, argumentos fora do JSON Schema, exceção na execução) em vez de derrubar a conexão.
- Resultado `dict` da tool vira `structuredContent`; outros tipos viram texto, porque o protocolo não transporta valores soltos.
- Listar tools **não** exige `WEATHER_API_KEY` — o `get_weather` só falha na execução. Há teste garantindo isso.
- Validação: 50 testes passando, `ruff check` limpo, e um cliente MCP real por HTTP (`streamablehttp_client` na porta 8131) listando `echo` e `get_weather`, invocando `echo` (`{'message': 'mcp funcionando'}`), invocando `get_weather('Curitiba')` contra a WeatherAPI real (`17.3 C, Parcialmente nublado, 72%`) e recebendo `isError=true` ao chamar tool inexistente.
