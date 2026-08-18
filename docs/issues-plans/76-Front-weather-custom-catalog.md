---
issue: 76
title: "[Front] -GOOGLE-A2UI- Register a custom catalog via BasicCatalogBase + A2UI_RENDERER_CONFIG"
branch: feat/a2ui-custom-catalog-75-77-humidity-gauge
status: closed
last_updated: 08-18-2026
---

# Issue #76 — Register a custom catalog via BasicCatalogBase + A2UI_RENDERER_CONFIG

## Objective
Registra um catálogo customizado do projeto (`WeatherCatalog`), carregando o componente `HumidityGauge` (issue #75), fornecido ao lado — não no lugar — do `BasicCatalog` já configurado na issue #52. O SDK suporta múltiplos catálogos simultâneos; `createSurface.catalogId` decide qual usar.

## Scope
- `catalogs/weather-catalog.ts` (novo): `WeatherCatalog extends BasicCatalogBase`, `id` próprio (`.../catalogs/weather/catalog.json`), `extraComponents: [humidityGaugeEntry]`
- `app.config.ts`: `provideA2Ui({ catalogs: [new BasicCatalog(), new WeatherCatalog()] })`
- `app/agui/a2ui_constants.py` (backend): `WEATHER_CATALOG_ID`, espelhando o `id` do frontend — necessário porque o agente real (issue #72) precisa mandar o `catalogId` certo pro cliente resolver `HumidityGauge`
- Reference: `docs/tutorial_A2UI/05-custom-catalogs-in-a2ui.md` (Passo 2)

## Decisões de implementação
- **`WEATHER_CATALOG_ID` duplicado entre frontend (`weather-catalog.ts`) e backend (`a2ui_constants.py`), com o mesmo valor literal.** O protocolo A2UI não tem um mecanismo de "descoberta" de catálogos — o `catalogId` é só uma string que o cliente casa contra os catálogos registrados localmente. Manter os dois lados com a mesma constante (comentada explicitamente um apontando pro outro) é a forma mais simples de evitar divergência, dado que backend e frontend são dois códigos-fonte separados (sem um pacote compartilhado entre eles neste monorepo).
- **`WeatherCatalog extends BasicCatalogBase` com `extraComponents`, não um catálogo do zero.** Reaproveita toda a mecânica de resolução de componentes/funções do `BasicCatalogBase` — o catálogo customizado só adiciona `HumidityGauge` aos componentes padrão já disponíveis (`Text`, `Card`, `Column`, `Button`, etc.), em vez de recriar um catálogo paralelo sem os componentes básicos.

## Status
> Atualizado em: 08-18-2026

- [x] `WeatherCatalog` registrado em `app.config.ts`, ao lado do `BasicCatalog`.
- [x] `WEATHER_CATALOG_ID` espelhado no backend (`a2ui_constants.py`), usado pelo `WeatherA2UiActivityAgent` (issue #72) a partir desta issue.
- [x] **Validação funcional:** `pytest` (backend) 123/123. `ng build`/`ng test` (frontend) — ver issue #77, onde o catálogo é exercitado de ponta a ponta pelo card real.

## Notes
- Implementado originalmente por sessão do Cursor (não commitado); esta issue documenta a versão reorganizada em branch própria.
