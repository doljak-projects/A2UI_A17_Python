import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ChatEvent, ChatMessage } from '../models/chat.models';
import {
  INITIAL_SSE_PARSER_STATE,
  feedSseParser,
  toChatEvent,
} from './sse-parser';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ChatService {
  private readonly chatUrl = `${environment.apiBaseUrl}/chat`;

  /**
   * Envia o histórico e expõe os eventos SSE como Observable.
   *
   * Usa `fetch` + `ReadableStream` porque o `HttpClient` do Angular não entrega
   * chunks incrementais do corpo da resposta.
   */
  send(messages: ChatMessage[]): Observable<ChatEvent> {
    return new Observable<ChatEvent>((subscriber) => {
      const controller = new AbortController();

      void this.streamResponse(messages, controller.signal, subscriber);

      return () => controller.abort();
    });
  }

  private async streamResponse(
    messages: ChatMessage[],
    signal: AbortSignal,
    subscriber: {
      next: (value: ChatEvent) => void;
      error: (err: unknown) => void;
      complete: () => void;
    },
  ): Promise<void> {
    try {
      const response = await fetch(this.chatUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'text/event-stream',
        },
        body: JSON.stringify({ messages }),
        signal,
      });

      if (!response.ok) {
        throw new Error(`Falha ao chamar o chat: HTTP ${response.status}`);
      }

      if (!response.body) {
        throw new Error('Resposta do chat sem corpo');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let parserState = INITIAL_SSE_PARSER_STATE;

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        const parsed = feedSseParser(chunk, parserState);
        parserState = parsed.state;

        for (const raw of parsed.events) {
          const event = toChatEvent(raw);
          if (event) {
            subscriber.next(event);
          }
        }
      }

      subscriber.complete();
    } catch (error) {
      if (signal.aborted || isAbortError(error)) {
        subscriber.complete();
        return;
      }
      subscriber.error(error);
    }
  }
}

function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError';
}
