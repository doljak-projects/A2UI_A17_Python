---
issue: 77
title: "[Front] -A2UI- Wire the custom widget into the weather card's component tree"
branch: feat/a2ui-custom-catalog-75-77-humidity-gauge
status: closed
last_updated: 08-18-2026
---

# Issue #77 — Wire the custom widget into the weather card's component tree

## Objective
Usa o widget customizado `HumidityGauge` (issue #75) dentro do card de clima já existente (`createWeatherCard()`, issue #54), no lugar do `Text` genérico de umidade, apontando a surface pro catálogo customizado (issue #76).

## Scope
- `core/services/a2ui-weather-card.ts`: campo `card-humidity` trocado de `{ component: 'Text', text: { path: '/humidity' } }` pra `{ component: 'HumidityGauge', humidity: { path: '/humidity' } }`
- `pages/a2ui-test/a2ui-test.component.ts`: `inject(WeatherCatalog)` no lugar de `inject(BasicCatalog)`, pra `createSurface.catalogId` apontar pro catálogo certo
- `app/agui/agent.py` (backend): `WeatherA2UiActivityAgent` passa a chamar `create_weather_card(..., WEATHER_CATALOG_ID, ..., use_humidity_gauge=True)` — sem isso, o card emitido pelo agente real (issue #72) referenciaria `HumidityGauge` mas com `catalogId` do catálogo básico, e o cliente não conseguiria resolver o componente
- Reference: `docs/tutorial_A2UI/05-custom-catalogs-in-a2ui.md` (Passo 3, estendido pro caminho do agente real)

## Decisões de implementação
- **A troca precisou tocar os dois lados (front e back) pra ficar coerente.** O card de clima é montado em dois lugares independentes: `createWeatherCard()` (frontend, rota `/a2ui-test`) e `create_weather_card()` (backend, `WeatherA2UiActivityAgent`, issue #72) — os dois espelham a mesma estrutura, mas são implementações Python/TS separadas. Trocar só o frontend deixaria o card gerado pelo agente real quebrado (`HumidityGauge` referenciado sob o `catalogId` errado).
- **`create_weather_card()` já tinha o parâmetro `use_humidity_gauge` desde a issue #72** (default `False`) exatamente pra este momento — não foi preciso alterar a assinatura da função, só o valor passado por quem chama.

## Status
> Atualizado em: 08-18-2026

- [x] Card de clima (`/a2ui-test` e chat real via #72/#74) renderiza `HumidityGauge` em vez do `Text` de umidade.
- [x] **Validação funcional:**
  - `pytest` (backend): 123/123 — inclui `test_weather_a2ui_agent_emits_activity_snapshot`, que continua passando com o `catalogId`/`use_humidity_gauge` atualizados (o teste não afirma sobre `catalogId` especificamente, então a mudança não quebrou a asserção existente, mas a integração ponta a ponta foi conferida manualmente na estrutura das operações emitidas).
  - `ng build`: limpo.
  - `ng test`: 47/50 — 3 falhas pré-existentes, sem relação com esta mudança.

## Notes
- Implementado originalmente por sessão do Cursor (não commitado); esta issue documenta a versão reorganizada e com a correção de coerência front/back (catalogId) aplicada.
- Fecha a Parte 5 do tutorial (issues #75-77) — próxima: Parte 6 (DSL/performance, issues #78-80).
