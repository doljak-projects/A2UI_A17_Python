import { Component } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CopilotKit, provideCopilotKit } from '@copilotkit/angular';
import { HttpAgent } from '@ag-ui/client';

import { environment } from '../../../environments/environment';
import { injectWeatherAgentStore } from './weather-agent-store';

@Component({ selector: 'app-weather-agent-store-host', template: '', standalone: true })
class HostComponent {
  readonly store = injectWeatherAgentStore();
}

describe('injectWeatherAgentStore', () => {
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

  it('registra o agente A2UI apontando pro endpoint de activity snapshot', () => {
    const agent = copilotKit.getAgent('weather-a2ui-agent');

    expect(agent).toBeInstanceOf(HttpAgent);
    expect((agent as HttpAgent).url).toBe(`${environment.apiBaseUrl}/agui/weather-a2ui-agent-demo`);
  });

  it('registra o agente MCP Apps apontando pro endpoint de activity snapshot mcp-apps', () => {
    const agent = copilotKit.getAgent('weather-mcp-apps-agent');

    expect(agent).toBeInstanceOf(HttpAgent);
    expect((agent as HttpAgent).url).toBe(
      `${environment.apiBaseUrl}/agui/weather-mcp-apps-agent-demo`,
    );
  });

  it('registra o agente weather-agent como HttpAgent apontando pro endpoint POST resumível', () => {
    const agent = copilotKit.getAgent('weather-agent');

    expect(agent).toBeInstanceOf(HttpAgent);
    expect((agent as HttpAgent).url).toBe(`${environment.apiBaseUrl}/agui/weather-tool-agent-demo`);
  });

  it('devolve um AgentStore com isRunning()/messages() como signals', () => {
    const store = fixture.componentInstance.store();

    expect(store.isRunning()).toBe(false);
    expect(store.messages()).toEqual([]);
  });

  it('não recria o agente numa segunda injeção (idempotente)', () => {
    const firstAgent = copilotKit.getAgent('weather-agent');

    const other = TestBed.createComponent(HostComponent);
    other.detectChanges();

    expect(copilotKit.getAgent('weather-agent')).toBe(firstAgent);
  });
});
