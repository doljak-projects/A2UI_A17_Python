export type ChatRole = 'system' | 'user' | 'assistant';

export interface ChatMessage {
  role: ChatRole;
  content: string;
}

/** Eventos SSE emitidos pelo `POST /api/chat` do backend. */
export type ChatEvent =
  | { type: 'delta'; text: string }
  | {
      type: 'tool_call';
      id: string;
      name: string;
      arguments: Record<string, unknown>;
    }
  | {
      type: 'tool_result';
      id: string;
      name: string;
      content: unknown;
      isError: boolean;
    }
  | { type: 'done'; text: string; rounds: number }
  | { type: 'error'; message: string };
