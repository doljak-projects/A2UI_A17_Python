---
issue: 54
title: "[Front] -A2UI- Model the A2UI weather card using the existing WeatherToolResult shape"
branch: feat/a2ui-weather-card-54-weathertoolresult
status: closed
last_updated: 08-17-2026
---

# Issue #54 — Model the A2UI weather card using the existing WeatherToolResult shape

## Objective
Trocar o dataset genérico do card da issue #53 (`title`/`subtitle`) pelo shape real de clima já estabelecido na issue #35 (`WeatherToolResult`: `city`, `temperature_c`, `description`, `humidity`), reaproveitando o tipo e o mock existentes em vez de duplicar um modelo novo.

## Scope
- Reaproveitar (importar, não redefinir) `WeatherToolResult` de `weather-tool-for-a2ui.ts` (issue #35) como o tipo de dado do helper A2UI
- Atualizar a árvore de componentes (issue #53) pra bindar 4 `Text` em `/city`, `/temperature_c`, `/description`, `/humidity` via `{ path: '...' }`
- Reference: `docs/tutorial_A2UI/03-google-a2ui-dynamic-ui.md` (Passo 3)

## Decisões de implementação

- **Renomeação do helper: `a2ui-simple-card.ts`/`createSimpleCard()` → `a2ui-weather-card.ts`/`createWeatherCard()`.** O card deixa de ser um exemplo genérico e passa a ser especificamente de clima — segue o padrão já usado no projeto pra arquivos de domínio (`weather-frontend-tool.ts`, `weather-agent-store.ts`). A `interface SimpleCardData` local foi removida; o parâmetro `data` agora é tipado como `WeatherToolResult` (importado de `weather-tool-for-a2ui.ts`), sem redefinir o shape.

- **Reaproveitado `buildMockWeatherResult(city)`, já existente (issue #48/#36)**, em vez de criar outro mock. `A2uiTestComponent` chama `buildMockWeatherResult('São Paulo')` — cidade fixa, já que ainda não há input de usuário nesse ponto do tutorial (fica pra além do escopo desta issue).

- **4 `Text` sem função de formatação.** Cada campo (`city`, `temperature_c`, `description`, `humidity`) vira um `Text` bindado via `{ path: '/campo' }`, sem `formatNumber` do catálogo nem unidade (`°C`, `%`) — a issue tem *learning scope* "Basic" e pede só o wiring do dado existente, não formatação. `temperature_c`/`humidity` são `number` no data model; o `TextComponent` do SDK aceita e interpola normalmente (`text = computed(() => props['text']?.value() || '')`, confirmado no `.mjs`), sem exigir string.

## Status
> Atualizado em: 2026-08-17

- [x] `createWeatherCard()` criado em `core/services/a2ui-weather-card.ts`, tipado com `WeatherToolResult`.
- [x] `A2uiTestComponent` atualizado pra usar `createWeatherCard(...)` + `buildMockWeatherResult('São Paulo')`.
- [x] `ng build` limpo (só warning de budget pré-existente). `ng test`: 46/49 verdes, mesmas 3 falhas pré-existentes de `chat.component.spec.ts`, sem regressão.
- [x] Verificação visual no browser: card exibe os 4 campos reais (`São Paulo` / `22` / `Parcialmente nublado` / `60`).

## Notes
- Nenhuma ação de cliente (`Button`/`onAction`) ainda — isso é a issue #55, que atualiza o card in-place via `updateDataModel` sem recriar a surface.
