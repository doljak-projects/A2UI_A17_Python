import { Signal, inject } from '@angular/core';
import { AgentStore, CopilotKit, injectAgentStore } from '@copilotkit/angular';
import { HttpAgent } from '@ag-ui/client';

import { environment } from '../../../environments/environment';

export const WEATHER_A2UI_AGENT_ID = 'weather-a2ui-agent';
const WEATHER_A2UI_AGENT_ENDPOINT = '/agui/weather-a2ui-agent-demo';

/**
 * Registra o agente AG-UI de clima em modo A2UI (issue #72, endpoint de
 * ACTIVITY_SNAPSHOT) no runtime do CopilotKit via `updateRuntime({ selfManagedAgents })`.
 * O chat sidecar (`copilot-weather-chat`) roda travado nesse modo — os modos
 * `tool`/`mcp-apps` que existiram nas issues #45-50/#84-87 foram removidos
 * daqui pra manter uma única rota de chat funcional.
 */
function initAgentStore(): void {
  const copilotKit = inject(CopilotKit);

  // Guard por instância de `CopilotKit` (não por módulo): cada bootstrap da
  // app — ou cada TestBed em teste — tem sua própria instância injetada.
  if (copilotKit.getAgent(WEATHER_A2UI_AGENT_ID)) {
    return;
  }

  copilotKit.updateRuntime({
    selfManagedAgents: {
      [WEATHER_A2UI_AGENT_ID]: new HttpAgent({
        url: `${environment.apiBaseUrl}${WEATHER_A2UI_AGENT_ENDPOINT}`,
      }),
    },
  });
}

/**
 * Ponto único de acesso ao agent store de clima A2UI: garante o registro via
 * `initAgentStore()` e devolve o `Signal<AgentStore>` (`messages()`/`isRunning()`)
 * do CopilotKit.
 */
export function injectWeatherAgentStore(): Signal<AgentStore> {
  initAgentStore();
  return injectAgentStore(WEATHER_A2UI_AGENT_ID);
}
