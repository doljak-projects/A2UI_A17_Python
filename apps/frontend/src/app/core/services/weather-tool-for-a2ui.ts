import { Tool } from '@ag-ui/core';
import { z } from 'zod/v4';

/**
 * Campos em snake_case propositalmente — casam com o JSON real emitido por
 * `get_weather` no backend (`app/schemas/weather.py`, `WeatherResult`), sem
 * precisar de uma camada de mapeamento quando o resultado real for
 * consumido (issue #36).
 */
export const weatherSchema = z.object({
  city: z.string(),
  temperature_c: z.number(),
  description: z.string(),
  humidity: z.number(),
});

export type WeatherToolResult = z.infer<typeof weatherSchema>;

export const showWeatherTool: Tool = {
  name: 'show_weather',
  description: 'Exibe as condições climáticas atuais de uma cidade.',
  parameters: z.toJSONSchema(weatherSchema),
};

/**
 * Valida e tipa o conteúdo bruto de um `ToolCallResultEvent`/`ToolMessage`
 * (JSON string) contra `weatherSchema`. Não renderiza nada — só prepara o
 * dado para quem for exibir o card de clima (`ChatComponent`, issue #36).
 */
export function parseWeatherToolResult(content: string): WeatherToolResult {
  return weatherSchema.parse(JSON.parse(content));
}
