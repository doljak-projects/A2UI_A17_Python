---
issue: 79
title: "[Back] -GOOGLE-A2UI- Deterministic DSL-to-A2UI conversion in the backend"
branch: feat/a2ui-dashboard-perf-78-80-dsl-cache
status: closed
last_updated: 08-18-2026
---

# Issue #79 — Deterministic DSL-to-A2UI conversion in the backend

## Objective
Implementa, em código Python puro (sem LLM), a conversão da DSL (issue #78) numa mensagem `updateComponents` real — reaproveitando o padrão de árvore achatada já usado em `create_weather_card()` (`Card`/`Column`/`Text`), um bloco de 4 campos por tile pedido.

## Scope
- `app/agui/dashboard_dsl.py`: `build_dashboard_components()` (DSL → lista achatada de componentes), `build_dashboard_data_model()` (lista de `WeatherResult` → `{ tiles: [...] }`), `build_dashboard_messages()` (monta as 3 mensagens A2UI completas)
- Reference: `docs/tutorial_A2UI/06-a2ui-dashboard-performance.md` (Passo 2)

## Decisões de implementação
- **Cada tile gera 4 IDs prefixados (`tile-{index}-city/temperature/description/humidity`)**, todos filhos de uma única `Column` (`dashboard-column`) sob o `Card` raiz — mesma estrutura achatada por referência de ID já estabelecida nas issues #53/#54, só que agora gerada em loop em vez de hardcoded.
- **Data binding via `path` indexado (`/tiles/{index}/city`, etc.)**, casando com o shape de `build_dashboard_data_model()` (`{ tiles: [WeatherResult, ...] }`) — cada tile lê seu próprio índice no array, sem precisar de um `updateDataModel` por tile.
- **`build_dashboard_components()` não busca dado nenhum** — só monta estrutura a partir da DSL (`WeatherDashboardDsl`). Buscar o clima de cada cidade (`get_weather`) é responsabilidade de quem chama (o agente, issue #78/#80), mantendo esta função pura e determinística — importante porque ela também é reaproveitada pelo cache (issue #80) sem repetir chamadas de API.

## Status
> Atualizado em: 08-18-2026

- [x] `build_dashboard_components()`/`build_dashboard_data_model()` implementados e determinísticos (mesma DSL → mesma estrutura, sempre).
- [x] **Validação funcional:** `pytest` — 125/125 no total do backend; a conversão é exercitada indiretamente por `test_weather_dashboard_agent_uses_cache_on_second_run` (issue #80), que confirma que a mesma DSL produz a mesma lista de `components` em duas execuções.

## Notes
- Implementado originalmente por sessão do Cursor (não commitado); esta issue documenta a versão reorganizada em branch própria.
