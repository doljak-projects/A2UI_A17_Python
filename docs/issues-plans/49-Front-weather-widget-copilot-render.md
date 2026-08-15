---
issue: 49
title: "[Front] -A2UI- Weather widget rendered via copilot-render-tool-calls"
branch: feat/weather-widget-49-copilot-render
status: closed
last_updated: 2026-08-15
---

# Issue #49 — Weather widget rendered via copilot-render-tool-calls

## Objective
Anexar um componente Angular (`WeatherWidget`, implementando `ToolRenderer`) à frontend tool `show_weather`, renderizado como card interativo no histórico do chat via `<copilot-render-tool-calls>`.

## Scope
- `WeatherWidgetComponent` com `ToolRenderer<{ city: string }>` (args da tool)
- Exibir loading enquanto `status !== 'complete'`; parsear `toolCall.result` com `parseWeatherToolResult` (issue #35) quando completo
- Registrar `component: WeatherWidgetComponent` em `registerFrontendTool` no `weather-agent-store.ts`
- Reference: `docs/tutorial_A2UI/02-ag-ui-copilotkit-angular.md` (Passo 5)

## Status
> Atualizado em: 2026-08-15

- [x] `WeatherWidgetComponent` criado em `apps/frontend/src/app/components/weather-widget/` — card Material com cidade, temperatura, descrição e umidade.
- [x] `weather-agent-store.ts` estendido: `component: WeatherWidgetComponent` na config de `show_weather`.
- [x] Spec `weather-widget.component.spec.ts` — 2 casos (loading + resultado parseado).

## Notes
- `ToolRenderer<Args>` tipa os *argumentos* da tool (`{ city }`), não o resultado — o widget parseia `toolCall.result` (JSON string) via `parseWeatherToolResult`.
- Consumido pela demo da issue #50 em `/copilot-weather-chat`.
