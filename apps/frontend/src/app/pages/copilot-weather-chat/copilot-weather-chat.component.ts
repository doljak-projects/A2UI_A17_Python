import { Component } from '@angular/core';
import { CopilotChat } from '@copilotkit/angular';

import {
  WEATHER_A2UI_AGENT_ID,
  injectWeatherAgentStore,
} from '../../core/services/weather-agent-store';

/**
 * Rota principal de chat do projeto (`/chat`), travada no modo A2UI
 * (issues #50/#72-74). Usa o componente pronto `<copilot-chat>` do
 * `@copilotkit/angular` (input, scroll, bolhas de mensagem e roteamento de
 * `activity` já vêm prontos do pacote) em vez da UI de chat feita à mão —
 * o roteamento de `activity` continua resolvendo pro `A2uiActivityRenderer`
 * (issue #73), registrado em `app.config.ts`.
 */
@Component({
  selector: 'app-copilot-weather-chat',
  imports: [CopilotChat],
  template: `<copilot-chat class="chat-a2ui" [agentId]="agentId" />`,
  styleUrl: './copilot-weather-chat.component.scss',
})
export class CopilotWeatherChatComponent {
  private readonly agentStore = injectWeatherAgentStore();

  readonly agentId = WEATHER_A2UI_AGENT_ID;
}
