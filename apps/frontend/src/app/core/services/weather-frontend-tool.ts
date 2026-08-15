import { z } from 'zod/v4';

export { buildMockWeatherResult } from './weather-tool-for-a2ui';

/**
 * Schema dos *argumentos* que a tool `show_weather` recebe do servidor
 * (`WeatherResumableToolCallAgent`, issue #45: `{"city": "..."}`) —
 * diferente do `weatherSchema` de `weather-tool-for-a2ui.ts`, que descreve o
 * *resultado* completo devolvido pela tool.
 */
export const weatherToolArgsSchema = z.object({
  city: z.string(),
});
