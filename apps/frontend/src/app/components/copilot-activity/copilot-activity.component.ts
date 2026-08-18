import { NgComponentOutlet } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, inject, input } from '@angular/core';
import type { AbstractAgent, ActivityMessage } from '@ag-ui/client';
import { CopilotKit } from '@copilotkit/angular';

/**
 * Roteia uma mensagem `role: 'activity'` para o `ActivityRenderer` registrado
 * no CopilotKit com base no `activityType` (issues #74/#87).
 */
@Component({
  selector: 'app-copilot-activity',
  imports: [NgComponentOutlet],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (rendererConfig(); as config) {
      <ng-container
        [ngComponentOutlet]="config.component"
        [ngComponentOutletInputs]="outletInputs()"
      />
    } @else {
      <p class="copilot-activity__unsupported">
        Atividade não suportada: <code>{{ message().activityType }}</code>
      </p>
    }
  `,
  styles: `
    :host {
      display: block;
      width: 100%;
    }

    .copilot-activity__unsupported {
      margin: 0;
      color: #991b1b;
      font-size: 0.9rem;
    }
  `,
})
export class CopilotActivityComponent {
  private readonly copilotKit = inject(CopilotKit);

  readonly message = input.required<ActivityMessage>();
  readonly agent = input<AbstractAgent>();
  readonly agentId = input<string>();

  protected readonly rendererConfig = computed(() =>
    this.copilotKit
      .activityMessageRenderConfigs()
      .find((config) => config.activityType === this.message().activityType),
  );

  protected readonly outletInputs = computed(() => {
    const message = this.message();
    const resolvedAgent =
      this.agent() ??
      (this.agentId() ? this.copilotKit.getAgent(this.agentId()!) : undefined);

    return {
      activityType: message.activityType,
      content: message.content,
      message,
      agent: resolvedAgent,
    };
  });
}
