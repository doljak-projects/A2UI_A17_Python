import { Component, inject, OnInit } from '@angular/core';
import { A2uiRendererService, BasicCatalog, SurfaceComponent } from '@a2ui/angular/v0_9';

import { createSimpleCard } from '../../core/services/a2ui-simple-card';

const SURFACE_ID = 'a2ui-test-surface';

/**
 * Ponto de entrada isolado da issue #53: ciclo mínimo createSurface ->
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
    const messages = createSimpleCard(SURFACE_ID, this.catalog.id, {
      title: 'Card estático A2UI',
      subtitle: 'Renderizado via createSurface / updateComponents / updateDataModel',
    });
    this.renderer.processMessages(messages);
  }
}
