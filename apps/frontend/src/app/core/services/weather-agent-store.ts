import { Signal, inject } from '@angular/core';
import { AgentStore, CopilotKit, injectAgentStore, registerFrontendTool } from '@copilotkit/angular';
import { HttpAgent } from '@ag-ui/client';

import { environment } from '../../../environments/environment';
import { buildMockWeatherResult, weatherToolArgsSchema } from './weather-frontend-tool';
import { WeatherWidgetComponent } from '../../components/weather-widget/weather-widget.component';

export const WEATHER_TOOL_AGENT_ID = 'weather-agent';
export const WEATHER_A2UI_AGENT_ID = 'weather-a2ui-agent';

/** Issue #72 acrescenta o modo `a2ui`; `mcp-apps` chega na issue #84. */
export type WeatherChatAgentMode = 'tool' | 'a2ui';

const AGENT_IDS: Record<WeatherChatAgentMode, string> = {
  tool: WEATHER_TOOL_AGENT_ID,
  a2ui: WEATHER_A2UI_AGENT_ID,
};

const AGENT_ENDPOINTS: Record<WeatherChatAgentMode, string> = {
  tool: '/agui/weather-tool-agent-demo',
  a2ui: '/agui/weather-a2ui-agent-demo',
};

/**
 * Registra os agentes AG-UI de clima (issue #45, endpoint POST resumível, e
 * issue #72, endpoint de ACTIVITY_SNAPSHOT A2UI) no runtime do CopilotKit via
 * `updateRuntime({ selfManagedAgents })`, e a tool `show_weather` (issue #48)
 * que o CopilotKit resolve sozinho durante `runAgent`.
 */
function initAgentStores(): void {
  const copilotKit = inject(CopilotKit);

  // Guard por instância de `CopilotKit` (não por módulo): cada bootstrap da
  // app — ou cada TestBed em teste — tem sua própria instância injetada.
  if (copilotKit.getAgent(WEATHER_TOOL_AGENT_ID)) {
    return;
  }

  const selfManagedAgents = Object.fromEntries(
    (Object.keys(AGENT_ENDPOINTS) as WeatherChatAgentMode[]).map((mode) => [
      AGENT_IDS[mode],
      new HttpAgent({
        url: `${environment.apiBaseUrl}${AGENT_ENDPOINTS[mode]}`,
      }),
    ]),
  );

  copilotKit.updateRuntime({ selfManagedAgents });

  registerFrontendTool({
    name: 'show_weather',
    description: 'Exibe as condições climáticas atuais de uma cidade.',
    parameters: weatherToolArgsSchema,
    component: WeatherWidgetComponent,
    agentId: WEATHER_TOOL_AGENT_ID,
    handler: async ({ city }) => buildMockWeatherResult(city),
  });
}

/**
 * Ponto único de acesso aos agent stores de clima: garante o registro via
 * `initAgentStores()` e devolve o `Signal<AgentStore>` (`messages()`/`isRunning()`)
 * do CopilotKit para o modo pedido (`tool` por padrão, compat com o uso
 * anterior à issue #72).
 */
export function injectWeatherAgentStore(
  mode: WeatherChatAgentMode = 'tool',
): Signal<AgentStore> {
  initAgentStores();
  return injectAgentStore(AGENT_IDS[mode]);
}
