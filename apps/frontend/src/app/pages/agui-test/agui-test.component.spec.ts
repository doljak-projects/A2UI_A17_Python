import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideNoopAnimations } from '@angular/platform-browser/animations';

import { AguiAgentService } from '../../core/services/agui-agent.service';
import { showWeatherTool } from '../../core/services/weather-tool-for-a2ui';
import { AguiTestComponent } from './agui-test.component';

class StubAgent {
  addMessage = jasmine.createSpy('addMessage');
  runAgent = jasmine.createSpy('runAgent').and.resolveTo(undefined);
}

class AguiAgentServiceStub {
  agent = new StubAgent();

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

  it('dispara addMessage e runAgent ao rodar o agente', async () => {
    await component.runAgent();

    expect(aguiAgentService.agent.addMessage).toHaveBeenCalledWith(
      jasmine.objectContaining({ role: 'user', content: jasmine.any(String) }),
    );
    expect(aguiAgentService.agent.runAgent).toHaveBeenCalledWith({ tools: [showWeatherTool] });
    expect(component.status()).toBe('done');
  });

  it('marca status como error se runAgent falhar', async () => {
    aguiAgentService.agent.runAgent.and.rejectWith(new Error('falhou'));

    await component.runAgent();

    expect(component.status()).toBe('error');
  });
});
