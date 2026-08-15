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
import { AssistantMessage } from '@ag-ui/client';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { CopilotKit, RenderToolCalls } from '@copilotkit/angular';

import { injectWeatherAgentStore } from '../../core/services/weather-agent-store';

const WEATHER_AGENT_ID = 'weather-agent';

/**
 * Demo isolada da issue #50: chat sidecar ligado ao agent store do CopilotKit
 * (`injectWeatherAgentStore`). Não integra com `ChatComponent`/`ChatService`.
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
    RenderToolCalls,
  ],
  templateUrl: './copilot-weather-chat.component.html',
  styleUrl: './copilot-weather-chat.component.scss',
})
export class CopilotWeatherChatComponent implements AfterViewChecked {
  private readonly copilotKit = inject(CopilotKit);
  private readonly agentStore = injectWeatherAgentStore();
  private shouldScroll = false;

  readonly weatherAgentId = WEATHER_AGENT_ID;
  readonly messages = computed(() => this.agentStore().messages());
  readonly isRunning = computed(() => this.agentStore().isRunning());
  readonly error = signal<string | null>(null);

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
