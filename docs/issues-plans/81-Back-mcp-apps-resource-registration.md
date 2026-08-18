---
issue: 81
title: "[Back] -MCP-APPS- Investigate MCP Apps support in the Python mcp SDK and register the weather tool's app resource"
branch: feat/mcp-apps-fundamentals-81-83-host-app
status: closed
last_updated: 08-18-2026
---

# Issue #81 — Investigate MCP Apps support in the Python mcp SDK and register the weather tool's app resource

## Objective
MCP Apps é declarativo: a metadata de uma tool MCP aponta (`resourceUri`) pra um widget HTML fixo, registrado de antemão. O artigo de referência usa o SDK JS/Node (`@modelcontextprotocol/ext-apps/server`); esta issue investiga se o SDK Python `mcp` (já usado em `app/mcp/server.py`, issue #7) tem equivalente nativo, e registra o recurso da tool `get_weather`.

## Scope
- `app/mcp/resources.py` (novo): `load_weather_app_html()` (lê o HTML, cacheado via `lru_cache`), `read_weather_app_resource(uri)` (valida o URI, devolve o recurso no formato MCP)
- `app/mcp/assets/weather_card.html` (novo): widget HTML puro (sem framework)
- `app/mcp/server.py`: `list_tools()` anota `get_weather` com `meta.ui.resourceUri`; novos handlers `list_resources()`/`read_resource()`
- `app/agui/a2ui_constants.py`: `WEATHER_MCP_RESOURCE_URI = "ui://weather/card.html"`
- Reference: `docs/tutorial_A2UI/07-mcp-apps-fundamentals.md` (Passo 1)

## Decisões de implementação
- **Resultado da investigação: o SDK Python `mcp` não tem uma extensão dedicada equivalente a `@modelcontextprotocol/ext-apps/server`** (sem `registerAppTool`/`registerAppResource`). A mecânica foi implementada manualmente usando a API de baixo nível já usada no projeto (`mcp.server.lowlevel.Server`, issue #7): `@server.list_resources()`/`@server.read_resource()` (nativos do `Server` — não são exclusivos de MCP Apps, fazem parte do protocolo MCP base) + o campo `meta` livre em `mcp.types.Tool`, onde a convenção `{ ui: { resourceUri } }` do spec MCP Apps foi replicada manualmente.
- **Bug real encontrado e corrigido: `read_resource(uri: str)` recebia um `pydantic.AnyUrl`, não uma `str`, apesar da assinatura do decorator declarar `str`.** `AnyUrl(...) == "..."` é sempre `False` (tipos diferentes), então a comparação `uri != WEATHER_MCP_RESOURCE_URI` disparava `KeyError` mesmo pro URI correto — só detectado ao testar via sessão MCP real (`create_connected_server_and_client_session`), não pelas funções Python isoladas. Corrigido com `str(uri)` antes de comparar.
- **`load_weather_app_html()` com `@lru_cache(maxsize=1)`** — o HTML é estático, não há motivo pra reler o arquivo do disco a cada requisição.

## Status
> Atualizado em: 08-18-2026

- [x] Investigação concluída e documentada (sem SDK dedicado em Python — implementação manual via API low-level).
- [x] `get_weather` anota `meta.ui.resourceUri`; `list_resources()`/`read_resource()` implementados.
- [x] **Bug de tipo `AnyUrl` vs `str` corrigido** — só descoberto porque o teste desta issue exercita o servidor MCP real via sessão in-memory (mesmo padrão de `test_mcp_server.py`), não só as funções isoladas.
- [x] **Validação funcional:** `pytest` — 129/129 no total do backend. `test_mcp_server_exposes_get_weather_ui_metadata_and_resource` confirma, via cliente MCP real: `get_weather` anuncia o `resourceUri`, o recurso aparece em `list_resources()`, e `read_resource()` devolve o HTML correto.

## Notes
- Implementado originalmente por sessão do Cursor (não commitado, com o bug de `AnyUrl` presente); esta issue documenta a versão reorganizada, com o bug corrigido e um teste que o teria pego desde o início.
