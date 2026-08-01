import {
  buildMockWeatherResult,
  createWeatherToolCallCapture,
  parseWeatherToolResult,
  showWeatherTool,
  weatherSchema,
} from './weather-tool-for-a2ui';

describe('weatherSchema', () => {
  it('aceita o formato real emitido por get_weather (snake_case)', () => {
    const result = weatherSchema.parse({
      city: 'São Paulo',
      temperature_c: 24.7,
      description: 'Ensolarado',
      humidity: 35,
    });

    expect(result).toEqual({
      city: 'São Paulo',
      temperature_c: 24.7,
      description: 'Ensolarado',
      humidity: 35,
    });
  });

  it('rejeita payload com campo faltando', () => {
    expect(() => weatherSchema.parse({ city: 'São Paulo' })).toThrow();
  });
});

describe('showWeatherTool', () => {
  it('expõe nome, descrição e o JSON Schema gerado a partir do weatherSchema', () => {
    expect(showWeatherTool.name).toBe('show_weather');
    expect(showWeatherTool.description).toContain('climáticas');
    expect(showWeatherTool.parameters).toEqual(
      jasmine.objectContaining({
        type: 'object',
        properties: jasmine.objectContaining({
          city: jasmine.any(Object),
          temperature_c: jasmine.any(Object),
          description: jasmine.any(Object),
          humidity: jasmine.any(Object),
        }),
      }),
    );
  });
});

describe('parseWeatherToolResult', () => {
  it('parseia e valida o JSON bruto de um ToolCallResultEvent', () => {
    const content = JSON.stringify({
      city: 'São Paulo',
      temperature_c: 24.7,
      description: 'Ensolarado',
      humidity: 35,
    });

    expect(parseWeatherToolResult(content)).toEqual({
      city: 'São Paulo',
      temperature_c: 24.7,
      description: 'Ensolarado',
      humidity: 35,
    });
  });

  it('lança erro para JSON malformado', () => {
    expect(() => parseWeatherToolResult('{not json')).toThrow();
  });

  it('lança erro para payload que não bate com o schema', () => {
    expect(() => parseWeatherToolResult(JSON.stringify({ city: 'São Paulo' }))).toThrow();
  });
});

describe('createWeatherToolCallCapture', () => {
  it('resolve a pending promise quando onToolCallEndEvent recebe show_weather', async () => {
    const { subscriber, pending } = createWeatherToolCallCapture();

    subscriber.onToolCallEndEvent!({
      event: { type: 'TOOL_CALL_END', toolCallId: 'tc-1' },
      toolCallName: 'show_weather',
      toolCallArgs: { city: 'São Paulo' },
    } as never);

    await expectAsync(pending).toBeResolvedTo({ toolCallId: 'tc-1', city: 'São Paulo' });
  });

  it('ignora eventos de outras tools', async () => {
    const { subscriber, pending } = createWeatherToolCallCapture();
    let settled = false;
    pending.then(() => (settled = true));

    subscriber.onToolCallEndEvent!({
      event: { type: 'TOOL_CALL_END', toolCallId: 'tc-2' },
      toolCallName: 'other_tool',
      toolCallArgs: {},
    } as never);

    await Promise.resolve();
    expect(settled).toBeFalse();
  });
});

describe('buildMockWeatherResult', () => {
  it('monta um resultado mockado para a cidade recebida', () => {
    expect(buildMockWeatherResult('Rio de Janeiro')).toEqual({
      city: 'Rio de Janeiro',
      temperature_c: 22,
      description: 'Parcialmente nublado',
      humidity: 60,
    });
  });
});
