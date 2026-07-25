import {
  AfterViewChecked,
  Component,
  ElementRef,
  OnDestroy,
  ViewChild,
  inject,
  signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Subscription } from 'rxjs';

import { ChatMessage } from '../../core/models/chat.models';
import { ChatService } from '../../core/services/chat.service';

export interface UiMessage {
  role: 'user' | 'assistant';
  content: string;
}

/** Milissegundos entre cada caractere renderizado (efeito typewriter). */
const TYPEWRITER_INTERVAL_MS = 18;

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    FormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss',
})
export class ChatComponent implements AfterViewChecked, OnDestroy {
  private readonly chatService = inject(ChatService);
  private streamSubscription?: Subscription;
  private shouldScroll = false;

  // --- typewriter ---
  private charQueue: string[] = [];
  private renderTimer: ReturnType<typeof setInterval> | null = null;
  private streamDone = false;

  readonly messages = signal<UiMessage[]>([]);
  readonly isStreaming = signal(false);
  readonly error = signal<string | null>(null);

  userInput = '';

  @ViewChild('scrollAnchor') private scrollAnchor?: ElementRef<HTMLDivElement>;

  ngAfterViewChecked(): void {
    if (!this.shouldScroll) return;
    this.scrollAnchor?.nativeElement.scrollIntoView({ behavior: 'smooth' });
    this.shouldScroll = false;
  }

  ngOnDestroy(): void {
    this.stopRenderLoop();
    this.streamSubscription?.unsubscribe();
  }

  send(): void {
    const text = this.userInput.trim();
    if (!text || this.isStreaming()) return;

    this.error.set(null);
    this.userInput = '';
    this.charQueue = [];
    this.streamDone = false;
    this.stopRenderLoop();

    this.messages.update((current) => [
      ...current,
      { role: 'user', content: text },
      { role: 'assistant', content: '' },
    ]);
    this.isStreaming.set(true);
    this.shouldScroll = true;

    const payload: ChatMessage[] = this.messages()
      .slice(0, -1)
      .map(({ role, content }) => ({ role, content }));

    this.streamSubscription?.unsubscribe();
    this.streamSubscription = this.chatService.send(payload).subscribe({
      next: (event) => {
        if (event.type === 'delta') {
          this.charQueue.push(...event.text.split(''));
          this.startRenderLoop();
        } else if (event.type === 'error') {
          this.error.set(event.message);
        }
      },
      error: (err: Error) => {
        this.error.set(err.message ?? 'Erro ao enviar mensagem');
        this.flushQueue();
        this.isStreaming.set(false);
      },
      complete: () => {
        this.streamDone = true;
      },
    });
  }

  private startRenderLoop(): void {
    if (this.renderTimer !== null) return;
    this.renderTimer = setInterval(() => {
      if (this.charQueue.length > 0) {
        const char = this.charQueue.shift()!;
        this.appendAssistantDelta(char);
      } else if (this.streamDone) {
        this.stopRenderLoop();
        this.isStreaming.set(false);
        this.shouldScroll = true;
      }
    }, TYPEWRITER_INTERVAL_MS);
  }

  private stopRenderLoop(): void {
    if (this.renderTimer !== null) {
      clearInterval(this.renderTimer);
      this.renderTimer = null;
    }
  }

  /** Descarrega a fila restante de uma vez (usada em caso de erro). */
  private flushQueue(): void {
    if (this.charQueue.length > 0) {
      this.appendAssistantDelta(this.charQueue.join(''));
      this.charQueue = [];
    }
    this.stopRenderLoop();
  }

  private appendAssistantDelta(text: string): void {
    this.messages.update((current) => {
      const copy = [...current];
      const last = copy[copy.length - 1];
      copy[copy.length - 1] = { ...last, content: last.content + text };
      return copy;
    });
    this.shouldScroll = true;
  }
}
