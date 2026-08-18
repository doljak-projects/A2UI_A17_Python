---
issue: 80
title: "[Back] -GOOGLE-A2UI- Cache the generated component structure by request hash"
branch: feat/a2ui-dashboard-perf-78-80-dsl-cache
status: closed
last_updated: 08-18-2026
---

# Issue #80 — Cache the generated component structure by request hash

## Objective
Cacheia a estrutura (`updateComponents`) do dashboard por um hash da DSL (issue #78), aproveitando a separação nativa do protocolo A2UI entre estrutura e dados: em cache-hit, a árvore de componentes é reaproveitada e só um `updateDataModel` novo é montado com dados frescos — a conversão DSL→A2UI (issue #79) é pulada inteiramente.

## Scope
- `app/agui/dashboard_cache.py` (novo): `DashboardStructureCache` (in-memory, por hash), `CachedDashboardStructure` (dataclass `dsl` + `components`), instância singleton `dashboard_structure_cache`
- `app/agui/agent.py`: nova classe `WeatherDashboardActivityAgent`, orquestrando DSL → cache → busca de dados → `ACTIVITY_SNAPSHOT` (com `content.cacheHit` sinalizando se houve reaproveitamento)
- `app/api/routes/agui.py`: nova rota `POST /api/agui/weather-dashboard-agent-demo`
- Reference: `docs/tutorial_A2UI/06-a2ui-dashboard-performance.md` (Passo 3)

## Decisões de implementação
- **Cache in-memory (dict Python), não Redis/persistente.** Suficiente pro escopo de demo do tutorial — o objetivo é demonstrar a técnica (separar cache de estrutura dos dados sempre-frescos), não montar infraestrutura de cache de produção.
- **`WeatherDashboardActivityAgent` reaproveita o mesmo `activityType: 'a2ui-surface'`** da issue #72, não um tipo novo — o dashboard é conceitualmente a mesma "atividade A2UI", só com mais tiles; o `A2uiActivityRenderer` (issue #73) já funciona sem alteração, sem precisar de um renderer dedicado.
- **`content.cacheHit` incluído no snapshot** só pra fins de demonstração/debug (visível no DevTools) — não é lido pelo cliente pra nenhuma lógica de renderização.
- **Sem chamada à tool call de validação via LLM.** Igual observado na issue #72, o agente monta tudo deterministicamente; a técnica de cache aqui reduz custo de *estrutura*, não elimina uma etapa de geração via LLM que este projeto nunca teve pra este fluxo.

## Status
> Atualizado em: 08-18-2026

- [x] `DashboardStructureCache` implementado; `WeatherDashboardActivityAgent` orquestra DSL → cache → dados → snapshot.
- [x] Rota `POST /api/agui/weather-dashboard-agent-demo` registrada.
- [x] **Validação funcional:** `pytest` — 125/125. `test_weather_dashboard_agent_uses_cache_on_second_run` confirma explicitamente: primeira run `cacheHit: false`, segunda run (mesma DSL) `cacheHit: true`, com a mesma lista de `components` nas duas.

## Notes
- Implementado originalmente por sessão do Cursor (não commitado); esta issue documenta a versão reorganizada em branch própria.
- Fecha a Parte 6 do tutorial (issues #78-80) — próxima: Parte 7 (fundamentos MCP Apps, issues #81-83).
