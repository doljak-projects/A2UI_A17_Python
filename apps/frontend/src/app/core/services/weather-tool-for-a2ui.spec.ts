import { parseWeatherToolResult, showWeatherTool, weatherSchema } from './weather-tool-for-a2ui';

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
