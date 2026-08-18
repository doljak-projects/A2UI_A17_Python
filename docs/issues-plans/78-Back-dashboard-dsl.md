---
issue: 78
title: "[Back] -GOOGLE-A2UI- Define a compact weather dashboard DSL instead of full A2UI markup"
branch: feat/a2ui-dashboard-perf-78-80-dsl-cache
status: closed
last_updated: 08-18-2026
---

# Issue #78 — Define a compact weather dashboard DSL instead of full A2UI markup

## Objective
Estabelece uma DSL compacta — em vez de fazer um LLM gerar markup A2UI completo token a token — como primeiro passo pra um dashboard multi-widget de clima. Também cria o cenário multi-tile que o projeto ainda não tinha (até aqui, só existia 1 card fixo).

## Scope
- `app/agui/dashboard_dsl.py` (novo): `WeatherDashboardTile`/`WeatherDashboardDsl` (Pydantic), `dsl_from_cities()`, `hash_dsl()`
- Reference: `docs/tutorial_A2UI/06-a2ui-dashboard-performance.md` (Passo 1)

## Decisões de implementação
- **DSL modelada com Pydantic (`BaseModel`), não um dict solto.** Reaproveita a mesma abordagem já usada nos schemas de request/response do backend (`app/schemas/`) — validação automática, e `model_dump()` pronto pra hashear/serializar.
- **`hash_dsl()` usa `json.dumps(..., sort_keys=True)` + SHA-256.** `sort_keys=True` garante que a mesma DSL semântica sempre produz o mesmo hash independente da ordem de inserção dos campos — importante já que o hash vira chave de cache na issue #80.
- **`TileType` restrito a `Literal["currentWeather"]`** por enquanto — a DSL é deliberadamente mínima nesta issue; tipos de tile adicionais (ex: previsão estendida) ficam fora de escopo.

## Status
> Atualizado em: 08-18-2026

- [x] `WeatherDashboardDsl`/`dsl_from_cities`/`hash_dsl` implementados.
- [x] **Validação funcional:** `pytest` — `test_dashboard_dsl_hash_is_stable` confirma que a mesma DSL produz sempre o mesmo hash. Exercitada de ponta a ponta pelas issues #79/#80 no mesmo PR.

## Notes
- Implementado originalmente por sessão do Cursor (não commitado); esta issue documenta a versão reorganizada em branch própria, encadeada sobre a Parte 5 (issues #75-77).
