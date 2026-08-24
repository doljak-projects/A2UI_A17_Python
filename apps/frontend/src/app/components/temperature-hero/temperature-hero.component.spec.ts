import { temperatureFeeling, weatherGlyph } from './temperature-hero.component';

describe('TemperatureHero helpers', () => {
  it('classifica a sensação térmica', () => {
    expect(temperatureFeeling(12)).toBe('frio');
    expect(temperatureFeeling(22)).toBe('ameno');
    expect(temperatureFeeling(30)).toBe('quente');
  });

  it('escolhe o glifo a partir da descrição', () => {
    expect(weatherGlyph('Parcialmente nublado', 22)).toBe('☁️');
    expect(weatherGlyph('Chuva fraca', 18)).toBe('🌧️');
    expect(weatherGlyph('Céu limpo', 27)).toBe('☀️');
  });
});
