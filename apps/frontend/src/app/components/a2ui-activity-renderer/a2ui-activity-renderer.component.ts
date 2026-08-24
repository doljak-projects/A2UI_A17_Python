import { ChangeDetectionStrategy, Component, computed, effect, inject, input } from '@angular/core';
import type { ActivityMessage } from '@ag-ui/client';
import type { A2uiMessage } from '@a2ui/web_core/v0_9';
import { A2uiRendererService, SurfaceComponent } from '@a2ui/angular/v0_9';
import type { ActivityRenderer, RenderActivityMessageConfig } from '@copilotkit/angular';
import { z } from 'zod';

export const A2UI_SURFACE_ACTIVITY_TYPE = 'a2ui-surface';

export const a2uiSurfaceContentSchema = z.object({
  operations: z.array(z.record(z.unknown())),
});

export type A2uiSurfaceContent = z.infer<typeof a2uiSurfaceContentSchema>;

function extractSurfaceId(operations: A2uiMessage[]): string | null {
  for (const message of operations) {
    if ('createSurface' in message) {
      return message.createSurface.surfaceId;
    }
    if ('updateComponents' in message) {
      return message.updateComponents.surfaceId;
    }
    if ('updateDataModel' in message) {
      return message.updateDataModel.surfaceId;
    }
  }
  return null;
}

/**
 * Renderer customizado de atividades A2UI (issue #73): delega as operações
 * recebidas no snapshot para o `A2uiRendererService` já configurado na app.
 */
@Component({
  selector: 'app-a2ui-activity-renderer',
  imports: [SurfaceComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (surfaceId(); as surface) {
      <div class="weather-surface">
        <a2ui-v09-surface [surfaceId]="surface" />
      </div>
    }
  `,
  styles: `
    :host {
      display: block;
      width: min(100%, 380px);
      max-width: 100%;
      color: #0f172a;
    }

    .weather-surface {
      overflow: hidden;
      padding: 16px;
      border-radius: 20px;
      background: #fff;
      border: 1px solid #e2e8f0;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
      color: #0f172a;
    }

    :host ::ng-deep {
      color: #0f172a;

      a2ui-v09-card,
      [role='group'] {
        background: transparent !important;
        color: inherit !important;
        box-shadow: none !important;
      }
    }
  `,
})
export class A2uiActivityRenderer implements ActivityRenderer<A2uiSurfaceContent> {
  private readonly renderer = inject(A2uiRendererService);

  readonly activityType = input.required<string>();
  readonly content = input.required<A2uiSurfaceContent>();
  readonly message = input.required<ActivityMessage>();
  readonly agent = input<import('@ag-ui/client').AbstractAgent>();

  protected readonly surfaceId = computed(() =>
    extractSurfaceId(this.content().operations as unknown as A2uiMessage[]),
  );

  constructor() {
    effect(() => {
      const operations = this.content().operations as unknown as A2uiMessage[];
      if (!operations?.length) return;
      try {
        this.renderer.processMessages(operations);
      } catch (error) {
        console.warn('A2UI processMessages failed', error);
      }
    });
  }
}

export const a2uiActivityRendererConfig: RenderActivityMessageConfig<A2uiSurfaceContent> = {
  activityType: A2UI_SURFACE_ACTIVITY_TYPE,
  content: {
    safeParse(content: unknown) {
      const parsed = a2uiSurfaceContentSchema.safeParse(content);
      return parsed.success
        ? { success: true, data: parsed.data }
        : { success: false, error: parsed.error };
    },
  },
  component: A2uiActivityRenderer,
};
