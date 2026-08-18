import {
  AfterViewChecked,
  Component,
  ElementRef,
  ViewChild,
  computed,
  inject,
  signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AssistantMessage, type ActivityMessage } from '@ag-ui/client';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { CopilotKit, RenderToolCalls } from '@copilotkit/angular';

import { CopilotActivityComponent } from '../../components/copilot-activity/copilot-activity.component';
import {
  WEATHER_A2UI_AGENT_ID,
  WEATHER_TOOL_AGENT_ID,
  injectWeatherAgentStore,
  type WeatherChatAgentMode,
} from '../../core/services/weather-agent-store';

/**
 * Demo das issues #50/#74: chat sidecar com suporte a mensagens `activity`
 * (card A2UI renderizado via `A2uiActivityRenderer`, issue #73) além do modo
 * de tool call client-side já existente (issue #45).
 */
@Component({
  selector: 'app-copilot-weather-chat',
  imports: [
    FormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatSelectModule,
    RenderToolCalls,
    CopilotActivityComponent,
  ],
  templateUrl: './copilot-weather-chat.component.html',
  styleUrl: './copilot-weather-chat.component.scss',
})
export class CopilotWeatherChatComponent implements AfterViewChecked {
  private readonly copilotKit = inject(CopilotKit);
  private readonly toolStore = injectWeatherAgentStore('tool');
  private readonly a2uiStore = injectWeatherAgentStore('a2ui');
  private shouldScroll = false;

  readonly agentMode = signal<WeatherChatAgentMode>('a2ui');
  readonly agentStore = computed(() =>
    this.agentMode() === 'tool' ? this.toolStore() : this.a2uiStore(),
  );
  readonly messages = computed(() => this.agentStore().messages());
  readonly isRunning = computed(() => this.agentStore().isRunning());
  readonly error = signal<string | null>(null);

  readonly activeAgentId = computed(() =>
    this.agentMode() === 'tool' ? WEATHER_TOOL_AGENT_ID : WEATHER_A2UI_AGENT_ID,
  );

  userInput = '';

  @ViewChild('scrollAnchor') private scrollAnchor?: ElementRef<HTMLDivElement>;

  ngAfterViewChecked(): void {
    if (!this.shouldScroll) return;
    this.scrollAnchor?.nativeElement.scrollIntoView({ behavior: 'smooth' });
    this.shouldScroll = false;
  }

  asAssistantMessage(message: unknown): AssistantMessage | null {
    return message && typeof message === 'object' && (message as AssistantMessage).role === 'assistant'
      ? (message as AssistantMessage)
      : null;
  }

  asActivityMessage(message: unknown): ActivityMessage | null {
    return message && typeof message === 'object' && (message as ActivityMessage).role === 'activity'
      ? (message as ActivityMessage)
      : null;
  }

  async send(): Promise<void> {
    const content = this.userInput.trim();
    if (!content || this.isRunning()) return;

    this.error.set(null);
    this.userInput = '';
    this.shouldScroll = true;

    const agent = this.agentStore().agent;
    agent.addMessage({
      id: crypto.randomUUID(),
      role: 'user',
      content,
    });

    try {
      await this.copilotKit.core.runAgent({ agent });
    } catch (err) {
      this.error.set(err instanceof Error ? err.message : 'Falha ao executar o agente');
    } finally {
      this.shouldScroll = true;
    }
  }
}
