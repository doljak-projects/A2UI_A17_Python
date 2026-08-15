import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CopilotKit, provideCopilotKit } from '@copilotkit/angular';

import { CopilotWeatherChatComponent } from './copilot-weather-chat.component';

describe('CopilotWeatherChatComponent', () => {
  let fixture: ComponentFixture<CopilotWeatherChatComponent>;
  let copilotKit: CopilotKit;
  let runAgentSpy: jasmine.Spy;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [CopilotWeatherChatComponent],
      providers: [provideCopilotKit({ defaultToolRendering: true })],
    });

    copilotKit = TestBed.inject(CopilotKit);
    runAgentSpy = spyOn(copilotKit.core, 'runAgent').and.resolveTo({} as never);

    fixture = TestBed.createComponent(CopilotWeatherChatComponent);
    fixture.detectChanges();
  });

  it('renderiza o título da demo', () => {
    const heading = fixture.nativeElement.querySelector('h2') as HTMLElement;
    expect(heading.textContent).toContain('issue #50');
  });

  it('envia mensagem do usuário e dispara runAgent', async () => {
    const component = fixture.componentInstance;
    const agent = copilotKit.getAgent('weather-agent')!;
    const addMessageSpy = spyOn(agent, 'addMessage').and.callThrough();
    component.userInput = 'Qual o clima em São Paulo?';

    await component.send();

    expect(addMessageSpy).toHaveBeenCalledWith(
      jasmine.objectContaining({
        role: 'user',
        content: 'Qual o clima em São Paulo?',
      }),
    );
    expect(runAgentSpy).toHaveBeenCalled();
  });

  it('não envia quando o input está vazio', async () => {
    const component = fixture.componentInstance;
    component.userInput = '   ';

    await component.send();

    expect(runAgentSpy).not.toHaveBeenCalled();
  });
});
