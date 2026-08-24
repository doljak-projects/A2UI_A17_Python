import { ChangeDetectionStrategy, Component, computed } from '@angular/core';
import { DynamicNumberSchema, DynamicStringSchema } from '@a2ui/web_core/v0_9';
import type { ComponentApi } from '@a2ui/web_core/v0_9';
import { CatalogComponent, type AngularComponentImplementation } from '@a2ui/angular/v0_9';
import { z } from 'zod';

export const humidityGaugeSchema = z
  .object({
    city: DynamicStringSchema,
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
      <p class="humidity-gauge__city">{{ city() }}</p>
      <div class="humidity-gauge__meta">
        <span class="humidity-gauge__title">Umidade</span>
        <span class="humidity-gauge__value">{{ value() }}% · {{ level() }}</span>
      </div>
      <div class="humidity-gauge__bar">
        <div class="humidity-gauge__fill" [style.width.%]="value()"></div>
      </div>
    </div>
  `,
  styles: `
    .humidity-gauge {
      display: grid;
      gap: 10px;
      padding: 16px 18px;
      border-radius: 16px;
      background: #f8fafc;
      color: #0f172a;
    }

    .humidity-gauge__city {
      margin: 0;
      font-size: 1.05rem;
      font-weight: 650;
      color: #0f172a;
    }

    .humidity-gauge__meta {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      font-size: 0.8rem;
    }

    .humidity-gauge__title {
      color: #64748b;
      font-weight: 600;
      letter-spacing: 0.03em;
      text-transform: uppercase;
    }

    .humidity-gauge__value {
      color: #0f172a;
      font-weight: 600;
    }

    .humidity-gauge__bar {
      height: 10px;
      border-radius: 999px;
      background: #e2e8f0;
      overflow: hidden;
    }

    .humidity-gauge__fill {
      height: 100%;
      background: linear-gradient(90deg, #7dd3fc, #2563eb);
      transition: width 150ms ease;
    }
  `,
})
export class HumidityGaugeComponent extends CatalogComponent<typeof humidityGaugeApi> {
  readonly city = computed(() => String(this.props().city.value() ?? ''));

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
