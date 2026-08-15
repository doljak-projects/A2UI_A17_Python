import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AngularToolCall } from '@copilotkit/angular';

import { WeatherWidgetComponent } from './weather-widget.component';

describe('WeatherWidgetComponent', () => {
  let fixture: ComponentFixture<WeatherWidgetComponent>;

  function createFixture(toolCall: AngularToolCall<{ city: string }>): void {
    fixture = TestBed.createComponent(WeatherWidgetComponent);
    fixture.componentRef.setInput('toolCall', toolCall);
    fixture.detectChanges();
  }

  it('mostra estado de carregamento enquanto a tool executa', () => {
    createFixture({
      args: { city: 'São Paulo' },
      status: 'executing',
      result: undefined,
    });

    const element = fixture.nativeElement as HTMLElement;
    expect(element.textContent).toContain('Consultando clima');
    expect(element.textContent).toContain('São Paulo');
  });

  it('renderiza o card com o resultado parseado quando a tool completa', () => {
    createFixture({
      args: { city: 'São Paulo' },
      status: 'complete',
      result: JSON.stringify({
        city: 'São Paulo',
        temperature_c: 22,
        description: 'Parcialmente nublado',
        humidity: 60,
      }),
    });

    const element = fixture.nativeElement as HTMLElement;
    expect(element.textContent).toContain('22°C');
    expect(element.textContent).toContain('Parcialmente nublado');
    expect(element.textContent).toContain('Umidade: 60%');
  });
});
