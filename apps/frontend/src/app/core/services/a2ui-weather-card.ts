import type { A2uiMessage } from '@a2ui/web_core/v0_9';

import type { WeatherToolResult } from './weather-tool-for-a2ui';

/** Nome da ação disparada pelo botão de refresh do card (issue #55). */
export const REFRESH_WEATHER_ACTION = 'refreshWeather';

/**
 * Monta o ciclo mínimo de mensagens A2UI (createSurface -> updateComponents ->
 * updateDataModel) para um card de clima, com os campos ligados ao data model
 * via `{ path }` em vez de valor embutido no componente. Reaproveita o shape
 * de `WeatherToolResult` (issue #35) — mesmos nomes de campo do JSON real
 * emitido por `get_weather` no backend.
 */
export function createWeatherCard(
  surfaceId: string,
  catalogId: string,
  data: WeatherToolResult,
): A2uiMessage[] {
  return [
    {
      version: 'v0.9',
      createSurface: { surfaceId, catalogId },
    },
    {
      version: 'v0.9',
      updateComponents: {
        surfaceId,
        components: [
          // `<a2ui-v09-surface>` renderiza por convenção o componente de id
          // 'root' (default de `SurfaceComponent.componentKey`), não infere
          // a raiz pela árvore de referências.
          { id: 'root', component: 'Card', child: 'card-column' },
          {
            id: 'card-column',
            component: 'Column',
            children: [
              'card-city',
              'card-temperature',
              'card-description',
              'card-humidity',
              'refresh-button',
            ],
          },
          {
            id: 'card-city',
            component: 'Text',
            variant: 'h3',
            text: { path: '/city' },
          },
          {
            id: 'card-temperature',
            component: 'Text',
            variant: 'body',
            text: { path: '/temperature_c' },
          },
          {
            id: 'card-description',
            component: 'Text',
            variant: 'body',
            text: { path: '/description' },
          },
          {
            id: 'card-humidity',
            component: 'HumidityGauge',
            humidity: { path: '/humidity' },
          },
          {
            id: 'refresh-button-label',
            component: 'Text',
            variant: 'body',
            text: 'Atualizar',
          },
          {
            id: 'refresh-button',
            component: 'Button',
            child: 'refresh-button-label',
            // `action.event.name` é o identificador que chega em `A2uiClientAction.name`
            // no handler de `renderer.surfaceGroup.onAction` (issue #55).
            action: { event: { name: REFRESH_WEATHER_ACTION } },
          },
        ],
      },
    },
    {
      version: 'v0.9',
      updateDataModel: { surfaceId, value: data },
    },
  ];
}

/**
 * Emite só a mensagem `updateDataModel`, sem recriar a surface nem a árvore
 * de componentes — usado para atualizar o card no lugar em resposta à ação
 * `refreshWeather` (issue #55).
 */
export function refreshWeatherCardData(surfaceId: string, data: WeatherToolResult): A2uiMessage[] {
  return [
    {
      version: 'v0.9',
      updateDataModel: { surfaceId, value: data },
    },
  ];
}
