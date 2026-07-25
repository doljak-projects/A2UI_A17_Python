import { ChatEvent } from '../models/chat.models';

export interface SseParserState {
  buffer: string;
  pendingEvent: string;
}

export const INITIAL_SSE_PARSER_STATE: SseParserState = {
  buffer: '',
  pendingEvent: '',
};

/** Frame SSE bruto antes de virar `ChatEvent`. */
export interface RawSseEvent {
  event: string;
  data: unknown;
}

/**
 * Acumula bytes decodificados e extrai frames SSE completos (linha a linha).
 * O backend envia `event:` + `data:` + linha em branco por frame.
 */
export function feedSseParser(
  chunk: string,
  state: SseParserState = INITIAL_SSE_PARSER_STATE,
): { events: RawSseEvent[]; state: SseParserState } {
  const events: RawSseEvent[] = [];
  state = { ...state, buffer: state.buffer + chunk };

  let newlineIndex = state.buffer.indexOf('\n');
  while (newlineIndex !== -1) {
    const line = state.buffer.slice(0, newlineIndex).replace(/\r$/, '');
    state.buffer = state.buffer.slice(newlineIndex + 1);

    if (line === '') {
      state.pendingEvent = '';
    } else if (line.startsWith('event: ')) {
      state.pendingEvent = line.slice('event: '.length).trim();
    } else if (line.startsWith('data: ')) {
      events.push({
        event: state.pendingEvent,
        data: JSON.parse(line.slice('data: '.length)),
      });
    }

    newlineIndex = state.buffer.indexOf('\n');
  }

  return { events, state };
}

/** Traduz o nome do evento SSE do backend para o union tipado do frontend. */
export function toChatEvent(raw: RawSseEvent): ChatEvent | null {
  const data = (raw.data ?? {}) as Record<string, unknown>;

  switch (raw.event) {
    case 'delta':
      return { type: 'delta', text: String(data['text'] ?? '') };
    case 'tool_call':
      return {
        type: 'tool_call',
        id: String(data['id'] ?? ''),
        name: String(data['name'] ?? ''),
        arguments: (data['arguments'] as Record<string, unknown>) ?? {},
      };
    case 'tool_result':
      return {
        type: 'tool_result',
        id: String(data['id'] ?? ''),
        name: String(data['name'] ?? ''),
        content: data['content'],
        isError: Boolean(data['is_error']),
      };
    case 'done':
      return {
        type: 'done',
        text: String(data['text'] ?? ''),
        rounds: Number(data['rounds'] ?? 0),
      };
    case 'error':
      return { type: 'error', message: String(data['message'] ?? 'Erro desconhecido') };
    default:
      return null;
  }
}
