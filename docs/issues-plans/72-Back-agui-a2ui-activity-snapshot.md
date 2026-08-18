---
issue: 72
title: "[Back] -AG-UI- Emit A2UI operations wrapped in an AG-UI ACTIVITY_SNAPSHOT from the weather agent"
branch: feat/a2ui-agui-integration-72-74-activity-snapshot
status: closed
last_updated: 08-18-2026
---

# Issue #72 — Emit A2UI operations wrapped in an AG-UI ACTIVITY_SNAPSHOT from the weather agent

## Objective
AG-UI não tem transporte oficial definido para mensagens A2UI. Esta issue embute as operações A2UI do card de clima (`createSurface`/`updateComponents`/`updateDataModel`, já usadas na rota isolada `/a2ui-test`, issues #53/#54) dentro de um evento AG-UI `ACTIVITY_SNAPSHOT`, emitido pelo backend `WeatherA2UiActivityAgent`, com `activityType: 'a2ui-surface'` identificando o payload pro cliente.

## Scope
- `app/agui/a2ui_weather_card.py` (novo): `create_weather_card()` — espelha `createWeatherCard()` do frontend, gerando as mesmas 3 mensagens A2UI em Python
- `app/agui/a2ui_constants.py` (novo): constantes compartilhadas (`BASIC_CATALOG_ID`, `A2UI_SURFACE_ACTIVITY_TYPE`, `REFRESH_WEATHER_ACTION`)
- `app/agui/agent.py`: nova classe `WeatherA2UiActivityAgent`, emitindo `RUN_STARTED` → `ACTIVITY_SNAPSHOT` (`content.operations`) → `RUN_FINISHED`
- `app/api/routes/agui.py`: nova rota `POST /api/agui/weather-a2ui-agent-demo`
- Reference: `docs/tutorial_A2UI/04-integrating-a2ui-with-ag-ui.md` (Passo 1)

## Decisões de implementação
- **`create_weather_card()` recebe `use_humidity_gauge: bool = False`.** O catálogo customizado com `HumidityGauge` só é registrado na issue #76 — nesta issue o campo de umidade usa `Text` simples, igual ao card original da #54. O parâmetro já existe pensando na extensão futura, sem acoplar #72 a um componente que ainda não existe no catálogo.
- **`ActivitySnapshotEvent` é uma classe real do SDK Python `ag_ui.core`** (`ag_ui.core.events.ActivitySnapshotEvent`), confirmada por import direto no venv — não é um tipo inventado; o SDK já suporta esse tipo de evento AG-UI.
- **Sem validação server-side via tool call ainda** (o artigo original também valida a estrutura A2UI gerada pelo LLM antes de emitir o snapshot) — como o `WeatherA2UiActivityAgent` monta o card de forma determinística (sem LLM gerando a estrutura), essa validação não se aplica aqui. Fica registrado como possível extensão futura no doc da Parte 4.

## Status
> Atualizado em: 08-18-2026

- [x] `create_weather_card()` implementado e testado isoladamente.
- [x] `WeatherA2UiActivityAgent` implementado, rota `POST /api/agui/weather-a2ui-agent-demo` registrada.
- [x] **Validação funcional:** `pytest` — 123/123 testes passam (inclui `test_create_weather_card_emits_three_protocol_messages` e `test_weather_a2ui_agent_emits_activity_snapshot`, cobrindo o parsing das 3 mensagens A2UI e a sequência `RUN_STARTED`/`ACTIVITY_SNAPSHOT`/`RUN_FINISHED`).
- [x] Integração ponta a ponta validada junto das issues #73/#74 (mesmo PR): o card renderiza no chat real via o snapshot emitido aqui.

## Notes
- Implementado originalmente por sessão do Cursor (não commitado); esta issue documenta a versão reorganizada/validada em branch própria, seguindo a convenção do projeto.
