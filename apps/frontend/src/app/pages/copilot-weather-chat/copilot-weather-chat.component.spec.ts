import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BasicCatalog, provideA2Ui, provideMarkdownRenderer } from '@a2ui/angular/v0_9';
import { CopilotKit, provideCopilotKit } from '@copilotkit/angular';
import { HttpAgent } from '@ag-ui/client';

import { a2uiActivityRendererConfig } from '../../components/a2ui-activity-renderer/a2ui-activity-renderer.component';
import { CopilotWeatherChatComponent } from './copilot-weather-chat.component';

describe('CopilotWeatherChatComponent', () => {
  let fixture: ComponentFixture<CopilotWeatherChatComponent>;
  let copilotKit: CopilotKit;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [CopilotWeatherChatComponent],
      providers: [
        provideCopilotKit({
          defaultToolRendering: true,
          renderActivityMessages: [a2uiActivityRendererConfig],
        }),
        provideA2Ui({ catalogs: [new BasicCatalog()] }),
        provideMarkdownRenderer(),
      ],
    });

    copilotKit = TestBed.inject(CopilotKit);
    fixture = TestBed.createComponent(CopilotWeatherChatComponent);
    fixture.detectChanges();
  });

  it('registra o agente A2UI ao montar a página', () => {
    const agent = copilotKit.getAgent('weather-a2ui-agent');

    expect(agent).toBeInstanceOf(HttpAgent);
  });

  it('renderiza o <copilot-chat> apontando pro agente A2UI', () => {
    const chat = fixture.nativeElement.querySelector('copilot-chat') as HTMLElement;

    expect(chat).toBeTruthy();
    expect(fixture.componentInstance.agentId).toBe('weather-a2ui-agent');
  });
});
