---
issue: 95
title: "[Back][Front] Detectar intenção de clima no chat e diferenciar card de temperatura vs. umidade"
branch: feat/weather-intent-95-intent-detection-and-temperature-hero
status: closed
last_updated: 08-24-2026
---

# Issue #95 — Detectar intenção de clima no chat e diferenciar card de temperatura vs. umidade

## Objective
Antes desta issue, `WeatherA2UiActivityAgent` sempre chamava `get_weather` pra São Paulo e sempre renderizava o mesmo card, mesmo quando o usuário só queria conversar. Agora o agente distingue conversa casual de pedido de clima, extrai a cidade da mensagem e escolhe o card (temperatura ou umidade) de acordo com a intenção detectada.

## Scope
- `app/agui/weather_intent.py` (novo): `has_weather_intent()`, `resolve_city()` e `resolve_card_kind()` a partir da última mensagem do usuário — regex de intenção (`clima`, `temperatura`, `umidade`, `°C`, etc.), heurística de extração de cidade removendo palavras de preenchimento (`_FILLER`), e fallback pra `DEFAULT_CITY` ("São Paulo").
- `app/agui/agent.py`: `WeatherA2UiActivityAgent` ganha dois caminhos —
  - sem intenção de clima: turno vai pro LLM normal (`_llm_turn`, via `HttpLLMClient`/`stream_tool_calling`), sem chamar `get_weather`;
  - com intenção: `_weather_turn` resolve cidade + tipo de card, consulta a WeatherAPI e emite `ActivitySnapshotEvent` com `cardKind` (`"weather"` ou `"humidity"`) no `content`.
- `app/agui/a2ui_weather_card.py`: reescrito para dois cards independentes com raiz própria — `create_weather_card()` (raiz `TemperatureHero`) e `create_humidity_card()` (raiz `HumidityGauge`) — no lugar do card único `Card > Column` com botão de refresh; `_surface_messages()` como helper compartilhado do ciclo `createSurface`/`updateComponents`/`updateDataModel`.
- `components/temperature-hero/` (novo, frontend): componente `TemperatureHero` no catálogo A2UI, paralelo ao `HumidityGauge` existente, pra exibir cidade + temperatura + descrição como card dedicado.
- `components/humidity-gauge/humidity-gauge.component.ts` e `components/a2ui-activity-renderer/a2ui-activity-renderer.component.ts`: ajustes pra acomodar o novo `cardKind` emitido pelo backend e a raiz de componente variável (antes sempre `Card`).
- `catalogs/weather-catalog.ts` e `core/services/a2ui-weather-card.ts`: registro do `TemperatureHero` e alinhamento com a nova forma dos dois cards.

## Decisões de implementação
- **Dois cards com raiz própria em vez de um card único condicional.** O card anterior (`Card > Column` com botão de refresh) tentava cobrir tempo e umidade ao mesmo tempo; separar em `create_weather_card()`/`create_humidity_card()` deixa cada card focado no que o usuário pediu, e simplifica o componente raiz do lado do frontend (`TemperatureHero` vs. `HumidityGauge`), sem precisar de lógica condicional dentro de um card genérico.
- **Botão de refresh removido dos dois cards novos.** Fazia sentido no card único da issue #55 (uma cidade fixa, ação de recarregar os mesmos dados); com o agente agora respondendo por intenção detectada a cada turno, o próprio chat já cobre o caso de "atualizar" (nova pergunta = novo turno).
- **Sem intenção de clima, o agente não chama `get_weather` nem monta card algum** — o turno vai inteiro pro LLM (`_llm_turn`), preservando o modo de conversa livre que existia antes da issue #72 sem forçar um card irrelevante em toda resposta.
- **`resolve_city()` cai em `DEFAULT_CITY` quando não consegue extrair nada útil** da mensagem (só filler words ou frase vazia após limpeza), evitando quebrar a chamada à WeatherAPI com uma cidade vazia.

## Status
> Atualizado em: 08-24-2026

- [x] Conversa casual (sem intenção de clima) não dispara `get_weather` nem card A2UI — vai pro LLM normalmente.
- [x] Pedido de clima/temperatura renderiza `TemperatureHero`; pedido de umidade renderiza `HumidityGauge`.
- [x] Cidade extraída da mensagem quando informada; cai em "São Paulo" como padrão.
- [x] **Validação:** `pytest` (backend) — inclui `test_weather_intent.py` (novo) e `test_agui_a2ui_activity.py` atualizado; `ng test`/`ng build` (frontend) — ver detalhes na PR.

## Notes
- Implementação já existia no working tree antes da issue ser aberta; issue criada para rastreio conforme o fluxo do projeto (branches/PR/doc por issue).
- Fecha com a PR correspondente à branch `feat/weather-intent-95-intent-detection-and-temperature-hero`.
