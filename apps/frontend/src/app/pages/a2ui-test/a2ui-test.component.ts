import { Component, inject, OnInit } from '@angular/core';
import { A2uiRendererService, BasicCatalog, SurfaceComponent } from '@a2ui/angular/v0_9';

import { createWeatherCard } from '../../core/services/a2ui-weather-card';
import { buildMockWeatherResult } from '../../core/services/weather-tool-for-a2ui';

const SURFACE_ID = 'a2ui-test-surface';

/**
 * Ponto de entrada isolado das issues #53/#54: ciclo mínimo createSurface ->
 * updateComponents -> updateDataModel do protocolo A2UI da Google, exibido
 * via <a2ui-v09-surface>. Não integra com nenhuma outra página.
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

  readonly surfaceId = SURFACE_ID;

  ngOnInit(): void {
    const messages = createWeatherCard(
      SURFACE_ID,
      this.catalog.id,
      buildMockWeatherResult('São Paulo'),
    );
    this.renderer.processMessages(messages);
  }
}
