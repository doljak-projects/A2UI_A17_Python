import { Component, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { AguiAgentService } from '../../core/services/agui-agent.service';
import { showWeatherTool } from '../../core/services/weather-tool-for-a2ui';

type RunStatus = 'idle' | 'running' | 'done' | 'error';

/**
 * Ponto de entrada isolado da issue #34: dispara `addMessage` + `runAgent`
 * contra `GET /api/agui/weather-tool-demo` só para validar o transporte
 * ponta a ponta (eventos aparecem no console via `aguiLogSubscriber`).
 * Desde a issue #35, registra `showWeatherTool` na chamada `runAgent`
 * (o endpoint de demo ainda não inspeciona `tools`, é só preparação).
 * Não integra com `ChatComponent`/`ChatService`.
 */
@Component({
  selector: 'app-agui-test',
  standalone: true,
  imports: [MatButtonModule, MatProgressSpinnerModule],
  templateUrl: './agui-test.component.html',
  styleUrl: './agui-test.component.scss',
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
      await agent.runAgent({ tools: [showWeatherTool] });
      this.status.set('done');
    } catch (err) {
      console.error('[AG-UI] runAgent falhou', err);
      this.status.set('error');
    }
  }
}
