import { TestBed } from '@angular/core/testing';

import { environment } from '../../../environments/environment';
import { AguiAgentService } from './agui-agent.service';
import { AguiGetHttpAgent } from './agui-get-http-agent';
import { aguiLogSubscriber } from './agui-log-subscriber';

describe('AguiAgentService', () => {
  let service: AguiAgentService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AguiAgentService);
  });

  it('cria um AguiGetHttpAgent apontando para o endpoint weather-tool-demo', () => {
    const agent = service.getAgent();

    expect(agent).toBeInstanceOf(AguiGetHttpAgent);
    expect(agent.url).toBe(`${environment.apiBaseUrl}/agui/weather-tool-demo`);
  });

  it('registra o aguiLogSubscriber no agente', () => {
    expect(service.getAgent().subscribers).toContain(aguiLogSubscriber);
  });

  it('devolve sempre a mesma instância (thread compartilhada)', () => {
    expect(service.getAgent()).toBe(service.getAgent());
  });

  it('pointAt troca a URL da instância compartilhada', () => {
    service.pointAt('/agui/demo');

    expect(service.getAgent().url).toBe(`${environment.apiBaseUrl}/agui/demo`);
  });
});
