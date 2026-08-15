import { Component } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CopilotKit, provideCopilotKit } from '@copilotkit/angular';

import { injectWeatherAgentStore } from './weather-agent-store';

@Component({ selector: 'app-weather-frontend-tool-host', template: '', standalone: true })
class HostComponent {
  readonly store = injectWeatherAgentStore();
}

describe('show_weather frontend tool', () => {
  let fixture: ComponentFixture<HostComponent>;
  let copilotKit: CopilotKit;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HostComponent],
      providers: [provideCopilotKit({})],
    });

    copilotKit = TestBed.inject(CopilotKit);
    fixture = TestBed.createComponent(HostComponent);
    fixture.detectChanges();
  });

  it('registra a tool show_weather para o agente weather-agent', () => {
    const tool = copilotKit.core.getTool({ toolName: 'show_weather', agentId: 'weather-agent' });

    expect(tool).toBeDefined();
    expect(tool?.name).toBe('show_weather');
  });

  it('o handler resolve a tool call com o mock de clima, sem precisar de uma segunda run manual', async () => {
    const tool = copilotKit.core.getTool({ toolName: 'show_weather', agentId: 'weather-agent' });

    const result = await tool?.handler?.({ city: 'São Paulo' }, {} as never);

    expect(result).toEqual({
      city: 'São Paulo',
      temperature_c: 22,
      description: 'Parcialmente nublado',
      humidity: 60,
    });
  });
});
