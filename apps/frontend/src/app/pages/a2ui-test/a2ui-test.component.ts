import { Component, DestroyRef, inject, OnInit } from '@angular/core';
import { A2uiRendererService, BasicCatalog, SurfaceComponent } from '@a2ui/angular/v0_9';

import {
  createWeatherCard,
  REFRESH_WEATHER_ACTION,
  refreshWeatherCardData,
} from '../../core/services/a2ui-weather-card';
import { buildMockWeatherResult } from '../../core/services/weather-tool-for-a2ui';

const SURFACE_ID = 'a2ui-test-surface';

// Alterna entre duas cidades mockadas a cada refresh, só para tornar visível
// que o card foi atualizado no lugar (issue #55) sem recriar a surface.
const REFRESH_CITIES = ['Rio de Janeiro', 'São Paulo'];

/**
 * Ponto de entrada isolado das issues #53/#54/#55: ciclo createSurface ->
 * updateComponents -> updateDataModel do protocolo A2UI da Google, exibido
 * via <a2ui-v09-surface>, com um botão que dispara updateDataModel in-place
 * via a ação `refreshWeather`. Não integra com nenhuma outra página.
 */
@Component({
  selector: 'app-a2ui-test',
  imports: [SurfaceComponent],
  templateUrl: './a2ui-test.component.html',
  styleUrl: './a2ui-test.component.scss',
})
export class A2uiTestComponent implements OnInit {
  private readonly renderer = inject(A2uiRendererService);
  private readonly catalog = inject(BasicCatalog);
  private readonly destroyRef = inject(DestroyRef);

  readonly surfaceId = SURFACE_ID;

  private nextRefreshCityIndex = 0;

  ngOnInit(): void {
    const messages = createWeatherCard(
      SURFACE_ID,
      this.catalog.id,
      buildMockWeatherResult('Curitiba'),
    );
    this.renderer.processMessages(messages);

    // `onAction` não é um Observable RxJS — é um EventSource próprio do SDK
    // (`.subscribe()` devolve um `Subscription` com `.unsubscribe()`), então
    // o cleanup é manual via `DestroyRef` em vez de `takeUntilDestroyed()`.
    const subscription = this.renderer.surfaceGroup.onAction.subscribe((action) => {
      if (action.surfaceId !== SURFACE_ID || action.name !== REFRESH_WEATHER_ACTION) return;

      const city = REFRESH_CITIES[this.nextRefreshCityIndex];
      this.nextRefreshCityIndex = (this.nextRefreshCityIndex + 1) % REFRESH_CITIES.length;

      this.renderer.processMessages(
        refreshWeatherCardData(SURFACE_ID, buildMockWeatherResult(city)),
      );
    });
    this.destroyRef.onDestroy(() => subscription.unsubscribe());
  }
}
