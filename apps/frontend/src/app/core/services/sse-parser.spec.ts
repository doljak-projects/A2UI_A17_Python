import { feedSseParser, toChatEvent } from './sse-parser';

describe('feedSseParser', () => {
  it('extrai um frame delta completo', () => {
    const input = 'event: delta\ndata: {"text":"Olá"}\n\n';
    const { events } = feedSseParser(input);

    expect(events).toEqual([{ event: 'delta', data: { text: 'Olá' } }]);
  });

  it('acumula chunks parciais até fechar o frame', () => {
    let state = feedSseParser('event: delta\n').state;
    let result = feedSseParser('data: {"text":"A"}\n\n', state);

    expect(result.events).toEqual([{ event: 'delta', data: { text: 'A' } }]);
  });

  it('processa múltiplos frames na mesma leitura', () => {
    const input =
      'event: delta\ndata: {"text":"A"}\n\n' +
      'event: done\ndata: {"text":"A","rounds":1}\n\n';

    const { events } = feedSseParser(input);

    expect(events.map((e) => e.event)).toEqual(['delta', 'done']);
  });
});

describe('toChatEvent', () => {
  it('mapeia delta, tool_call, tool_result, done e error', () => {
    expect(toChatEvent({ event: 'delta', data: { text: 'x' } })).toEqual({
      type: 'delta',
      text: 'x',
    });

    expect(
      toChatEvent({
        event: 'tool_call',
        data: { id: 'c1', name: 'get_weather', arguments: { city: 'SP' } },
      }),
    ).toEqual({
      type: 'tool_call',
      id: 'c1',
      name: 'get_weather',
      arguments: { city: 'SP' },
    });

    expect(
      toChatEvent({
        event: 'tool_result',
        data: { id: 'c1', name: 'get_weather', content: { temp: 20 }, is_error: false },
      }),
    ).toEqual({
      type: 'tool_result',
      id: 'c1',
      name: 'get_weather',
      content: { temp: 20 },
      isError: false,
    });

    expect(
      toChatEvent({ event: 'done', data: { text: 'pronto', rounds: 2 } }),
    ).toEqual({ type: 'done', text: 'pronto', rounds: 2 });

    expect(toChatEvent({ event: 'error', data: { message: 'falhou' } })).toEqual({
      type: 'error',
      message: 'falhou',
    });
  });

  it('ignora eventos desconhecidos', () => {
    expect(toChatEvent({ event: 'ping', data: {} })).toBeNull();
  });
});
