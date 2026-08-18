import { ChangeDetectionStrategy, Component, computed } from '@angular/core';
import { DynamicNumberSchema } from '@a2ui/web_core/v0_9';
import type { ComponentApi } from '@a2ui/web_core/v0_9';
import { CatalogComponent, type AngularComponentImplementation } from '@a2ui/angular/v0_9';
import { z } from 'zod';

export const humidityGaugeSchema = z
  .object({
    humidity: DynamicNumberSchema,
  })
  .strict();

export const humidityGaugeApi = {
  name: 'HumidityGauge',
  schema: humidityGaugeSchema,
} satisfies ComponentApi;

@Component({
  selector: 'app-humidity-gauge',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="humidity-gauge" role="meter" [attr.aria-valuenow]="value()">
      <div class="humidity-gauge__bar">
        <div class="humidity-gauge__fill" [style.width.%]="value()"></div>
      </div>
      <p class="humidity-gauge__label">{{ value() }}% — {{ level() }}</p>
    </div>
  `,
  styles: `
    .humidity-gauge {
      display: grid;
      gap: 6px;
    }

    .humidity-gauge__bar {
      height: 8px;
      border-radius: 999px;
      background: #e5e7eb;
      overflow: hidden;
    }

    .humidity-gauge__fill {
      height: 100%;
      background: linear-gradient(90deg, #38bdf8, #2563eb);
      transition: width 150ms ease;
    }

    .humidity-gauge__label {
      margin: 0;
      font-size: 0.85rem;
      color: #52525b;
    }
  `,
})
export class HumidityGaugeComponent extends CatalogComponent<typeof humidityGaugeApi> {
  readonly value = computed(() => {
    const humidity = this.props().humidity.value();
    return Math.max(0, Math.min(100, Math.round(humidity)));
  });

  readonly level = computed(() => {
    const humidity = this.value();
    if (humidity < 40) return 'baixa';
    if (humidity < 70) return 'moderada';
    return 'alta';
  });
}

export const humidityGaugeEntry: AngularComponentImplementation = {
  name: 'HumidityGauge',
  schema: humidityGaugeSchema,
  component: HumidityGaugeComponent,
};
