import { Injectable } from '@angular/core';

import { environment } from '../../../environments/environment';
import { AguiGetHttpAgent } from './agui-get-http-agent';
import { aguiLogSubscriber } from './agui-log-subscriber';

/**
 * Ponto único de acesso ao agente AG-UI (issue #34). `providedIn: 'root'`
 * garante uma única instância/thread compartilhada entre quem injetar este
 * serviço, em vez de cada consumidor criar seu próprio `HttpAgent`.
 */
@Injectable({ providedIn: 'root' })
export class AguiAgentService {
  private readonly agent = new AguiGetHttpAgent({
    url: `${environment.apiBaseUrl}/agui/weather-tool-demo`,
    threadId: crypto.randomUUID(),
  });

  constructor() {
    this.agent.subscribe(aguiLogSubscriber);
  }

  getAgent(): AguiGetHttpAgent {
    return this.agent;
  }

  /**
   * Aponta a instância compartilhada do agente para outro endpoint AG-UI do
   * backend (ex: alternar entre demos ao longo de um ciclo de duas runs,
   * issue #36). O `AguiGetHttpAgent` já sobrescreve `requestInit()` para
   * `GET` sem corpo, então só a URL muda entre chamadas.
   */
  pointAt(path: string): void {
    this.agent.url = `${environment.apiBaseUrl}${path}`;
  }
}
