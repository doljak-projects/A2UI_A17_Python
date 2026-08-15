import { Signal, inject } from '@angular/core';
import { AgentStore, CopilotKit, injectAgentStore } from '@copilotkit/angular';
import { HttpAgent } from '@ag-ui/client';

import { environment } from '../../../environments/environment';

const WEATHER_AGENT_ID = 'weather-agent';

/**
 * Registra o agente AG-UI de clima (issue #45, endpoint POST resumível) no
 * runtime do CopilotKit via `updateRuntime({ selfManagedAgents })`. O SDK não
 * exige nenhum override de `HttpAgent` aqui — diferente do `AguiGetHttpAgent`
 * (issue #34), esse endpoint já aceita o POST padrão do próprio SDK.
 */
function initAgentStore(): void {
  const copilotKit = inject(CopilotKit);

  if (copilotKit.getAgent(WEATHER_AGENT_ID)) {
    return;
  }

  copilotKit.updateRuntime({
    selfManagedAgents: {
      [WEATHER_AGENT_ID]: new HttpAgent({
        url: `${environment.apiBaseUrl}/agui/weather-tool-agent-demo`,
      }),
    },
  });
}

/**
 * Ponto único de acesso ao agent store de clima: garante o registro via
 * `initAgentStore()` e devolve o `Signal<AgentStore>` (`messages()`/`isRunning()`)
 * do CopilotKit para o agente registrado.
 */
export function injectWeatherAgentStore(): Signal<AgentStore> {
  initAgentStore();
  return injectAgentStore(WEATHER_AGENT_ID);
}
