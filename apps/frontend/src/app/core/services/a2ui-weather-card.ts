import type { A2uiMessage } from '@a2ui/web_core/v0_9';

import type { WeatherToolResult } from './weather-tool-for-a2ui';

/** Nome da ação disparada pelo botão de refresh do card (issue #55). */
export const REFRESH_WEATHER_ACTION = 'refreshWeather';

function surfaceMessages(
  surfaceId: string,
  catalogId: string,
  components: Record<string, unknown>[],
  data: WeatherToolResult,
): A2uiMessage[] {
  return [
    {
      version: 'v0.9',
      createSurface: { surfaceId, catalogId },
    },
    {
      version: 'v0.9',
      updateComponents: { surfaceId, components },
    },
    {
      version: 'v0.9',
      updateDataModel: { surfaceId, value: data },
    },
  ];
}

/**
 * Card de tempo: TemperatureHero como raiz. O agente escolhe este card quando
 * a pergunta é sobre clima/temperatura.
 */
export function createWeatherCard(
  surfaceId: string,
  catalogId: string,
  data: WeatherToolResult,
): A2uiMessage[] {
  return surfaceMessages(
    surfaceId,
    catalogId,
    [
      {
        id: 'root',
        component: 'TemperatureHero',
        city: { path: '/city' },
        temperature: { path: '/temperature_c' },
        description: { path: '/description' },
      },
    ],
    data,
  );
}

/**
 * Card de umidade: HumidityGauge como raiz. O agente escolhe este card quando
 * a pergunta fala de umidade.
 */
export function createHumidityCard(
  surfaceId: string,
  catalogId: string,
  data: WeatherToolResult,
): A2uiMessage[] {
  return surfaceMessages(
    surfaceId,
    catalogId,
    [
      {
        id: 'root',
        component: 'HumidityGauge',
        city: { path: '/city' },
        humidity: { path: '/humidity' },
      },
    ],
    data,
  );
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
