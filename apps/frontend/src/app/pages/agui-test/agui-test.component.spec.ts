import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideNoopAnimations } from '@angular/platform-browser/animations';

import { AguiAgentService } from '../../core/services/agui-agent.service';
import { showWeatherTool } from '../../core/services/weather-tool-for-a2ui';
import { AguiTestComponent } from './agui-test.component';

class StubAgent {
  addMessage = jasmine.createSpy('addMessage');
  runAgent = jasmine
    .createSpy('runAgent')
    .and.callFake(async (_params?: unknown, subscriber?: { onToolCallEndEvent?: Function }) => {
      subscriber?.onToolCallEndEvent?.({
        event: { type: 'TOOL_CALL_END', toolCallId: 'tc-stub' },
        toolCallName: 'show_weather',
        toolCallArgs: { city: 'São Paulo' },
      });
    });
}

class AguiAgentServiceStub {
  agent = new StubAgent();
  pointAt = jasmine.createSpy('pointAt');

  getAgent() {
    return this.agent;
  }
}

describe('AguiTestComponent', () => {
  let fixture: ComponentFixture<AguiTestComponent>;
  let component: AguiTestComponent;
  let aguiAgentService: AguiAgentServiceStub;

  beforeEach(async () => {
    aguiAgentService = new AguiAgentServiceStub();

    await TestBed.configureTestingModule({
      imports: [AguiTestComponent],
      providers: [
        provideNoopAnimations(),
        { provide: AguiAgentService, useValue: aguiAgentService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AguiTestComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('status inicial é idle', () => {
    expect(component.status()).toBe('idle');
  });

  it('percorre o ciclo de duas runs: aponta os endpoints, dispara as duas runAgent e monta a ToolMessage', async () => {
    await component.runAgent();

    expect(aguiAgentService.pointAt).toHaveBeenCalledWith('/agui/weather-tool-client-demo');
    expect(aguiAgentService.pointAt).toHaveBeenCalledWith('/agui/demo');

    expect(aguiAgentService.agent.addMessage).toHaveBeenCalledWith(
      jasmine.objectContaining({ role: 'user', content: jasmine.any(String) }),
    );
    expect(aguiAgentService.agent.addMessage).toHaveBeenCalledWith(
      jasmine.objectContaining({
        role: 'tool',
        toolCallId: 'tc-stub',
        content: JSON.stringify({
          city: 'São Paulo',
          temperature_c: 22,
          description: 'Parcialmente nublado',
          humidity: 60,
        }),
      }),
    );

    expect(aguiAgentService.agent.runAgent).toHaveBeenCalledTimes(2);
    expect(aguiAgentService.agent.runAgent.calls.argsFor(0)[0]).toEqual({
      tools: [showWeatherTool],
    });
    expect(component.status()).toBe('done');
  });

  it('marca status como error se a 1ª runAgent falhar', async () => {
    aguiAgentService.agent.runAgent.and.rejectWith(new Error('falhou'));

    await component.runAgent();

    expect(component.status()).toBe('error');
  });
});
