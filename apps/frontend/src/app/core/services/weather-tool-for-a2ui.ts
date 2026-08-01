import { AgentSubscriber } from '@ag-ui/client';
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

export interface PendingWeatherToolCall {
  toolCallId: string;
  city: string;
}

/**
 * Monta um `AgentSubscriber` "de uma run só" (segundo parâmetro de
 * `agent.runAgent(params, subscriber)`) para capturar a tool call
 * `show_weather` pendente, sem mexer nos subscribers permanentes
 * (`aguiLogSubscriber`). `onToolCallEndEvent` já entrega `toolCallArgs`
 * parseado pelo próprio SDK — não precisa parsear JSON manualmente.
 */
export function createWeatherToolCallCapture(): {
  subscriber: AgentSubscriber;
  pending: Promise<PendingWeatherToolCall>;
} {
  let resolvePending!: (value: PendingWeatherToolCall) => void;
  const pending = new Promise<PendingWeatherToolCall>((resolve) => {
    resolvePending = resolve;
  });

  const subscriber: AgentSubscriber = {
    onToolCallEndEvent({ event, toolCallName, toolCallArgs }) {
      if (toolCallName !== showWeatherTool.name) return;
      resolvePending({ toolCallId: event.toolCallId, city: String(toolCallArgs['city']) });
    },
  };

  return { subscriber, pending };
}

/**
 * "Executa" a ação local pedida pela tool call client-side: não há API de
 * clima disponível no browser, então monta um resultado mockado a partir da
 * cidade recebida nos args do servidor (issue #36).
 */
export function buildMockWeatherResult(city: string): WeatherToolResult {
  return {
    city,
    temperature_c: 22,
    description: 'Parcialmente nublado',
    humidity: 60,
  };
}
