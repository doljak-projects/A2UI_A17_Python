import { AfterViewChecked, Component, ElementRef, ViewChild, inject, signal } from '@angular/core';
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
export class ChatComponent implements AfterViewChecked {
  private readonly chatService = inject(ChatService);
  private streamSubscription?: Subscription;
  private shouldScroll = false;

  readonly messages = signal<UiMessage[]>([]);
  readonly isStreaming = signal(false);
  readonly error = signal<string | null>(null);

  userInput = '';

  @ViewChild('scrollAnchor') private scrollAnchor?: ElementRef<HTMLDivElement>;

  ngAfterViewChecked(): void {
    if (!this.shouldScroll) {
      return;
    }
    this.scrollAnchor?.nativeElement.scrollIntoView({ behavior: 'smooth' });
    this.shouldScroll = false;
  }

  send(): void {
    const text = this.userInput.trim();
    if (!text || this.isStreaming()) {
      return;
    }

    this.error.set(null);
    this.userInput = '';
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
          this.appendAssistantDelta(event.text);
        } else if (event.type === 'error') {
          this.error.set(event.message);
        }
      },
      error: (err: Error) => {
        this.error.set(err.message ?? 'Erro ao enviar mensagem');
        this.isStreaming.set(false);
      },
      complete: () => {
        this.isStreaming.set(false);
        this.shouldScroll = true;
      },
    });
  }

  private appendAssistantDelta(text: string): void {
    this.messages.update((current) => {
      const copy = [...current];
      const lastIndex = copy.length - 1;
      const last = copy[lastIndex];
      copy[lastIndex] = { ...last, content: last.content + text };
      return copy;
    });
    this.shouldScroll = true;
  }
}
