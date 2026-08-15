import { Component, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { AguiAgentService } from '../../core/services/agui-agent.service';
import {
  buildMockWeatherResult,
  createWeatherToolCallCapture,
  showWeatherTool,
} from '../../core/services/weather-tool-for-a2ui';

type RunStatus = 'idle' | 'running' | 'done' | 'error';

/**
 * Ponto de entrada isolado da issue #34, estendido na #36 para o ciclo de
 * duas runs de tool call client-side:
 * 1) `GET /api/agui/weather-tool-client-demo` — pede a tool call `show_weather`
 * 2) cliente "executa" localmente (dado mockado) e monta a `ToolMessage`
 * 3) `GET /api/agui/demo` — 2ª run, texto simples (o backend não vê o
 *    resultado de fato; ver `## Decisão de arquitetura` no doc da #36)
 * Eventos aparecem no console via `aguiLogSubscriber`.
 * Não integra com `ChatComponent`/`ChatService`.
 */
@Component({
    selector: 'app-agui-test',
    imports: [MatButtonModule, MatProgressSpinnerModule],
    templateUrl: './agui-test.component.html',
    styleUrl: './agui-test.component.scss'
})
export class AguiTestComponent {
  private readonly aguiAgentService = inject(AguiAgentService);

  readonly status = signal<RunStatus>('idle');

  async runAgent(): Promise<void> {
    this.status.set('running');

    const agent = this.aguiAgentService.getAgent();
    agent.addMessage({
      id: crypto.randomUUID(),
      role: 'user',
      content: 'Qual o clima em São Paulo?',
    });

    try {
      this.aguiAgentService.pointAt('/agui/weather-tool-client-demo');
      const { subscriber, pending } = createWeatherToolCallCapture();
      await agent.runAgent({ tools: [showWeatherTool] }, subscriber);

      const { toolCallId, city } = await pending;
      const result = buildMockWeatherResult(city);
      agent.addMessage({
        id: crypto.randomUUID(),
        role: 'tool',
        toolCallId,
        content: JSON.stringify(result),
      });

      this.aguiAgentService.pointAt('/agui/demo');
      await agent.runAgent();

      this.status.set('done');
    } catch (err) {
      console.error('[AG-UI] runAgent falhou', err);
      this.status.set('error');
    }
  }
}
