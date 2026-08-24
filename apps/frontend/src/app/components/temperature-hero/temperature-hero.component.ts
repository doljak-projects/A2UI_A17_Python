import { ChangeDetectionStrategy, Component, computed } from '@angular/core';
import { DynamicNumberSchema, DynamicStringSchema } from '@a2ui/web_core/v0_9';
import type { ComponentApi } from '@a2ui/web_core/v0_9';
import { CatalogComponent, type AngularComponentImplementation } from '@a2ui/angular/v0_9';
import { z } from 'zod';

export const temperatureHeroSchema = z
  .object({
    city: DynamicStringSchema,
    temperature: DynamicNumberSchema,
    description: DynamicStringSchema,
  })
  .strict();

export const temperatureHeroApi = {
  name: 'TemperatureHero',
  schema: temperatureHeroSchema,
} satisfies ComponentApi;

export type TemperatureFeeling = 'frio' | 'ameno' | 'quente';

export function temperatureFeeling(celsius: number): TemperatureFeeling {
  if (celsius < 18) return 'frio';
  if (celsius < 26) return 'ameno';
  return 'quente';
}

export function weatherGlyph(description: string, celsius: number): string {
  const text = description.toLowerCase();
  if (/chuva|rain|drizzle/.test(text)) return '🌧️';
  if (/tempestade|storm|thunder/.test(text)) return '⛈️';
  if (/neve|snow/.test(text)) return '❄️';
  if (/n[eé]voa|fog|mist/.test(text)) return '🌫️';
  if (/nublado|cloud|overcast/.test(text)) return '☁️';
  if (/sol|sunny|clear|c[eé]u limpo/.test(text)) return '☀️';
  return temperatureFeeling(celsius) === 'quente' ? '🌤️' : '🌥️';
}

@Component({
  selector: 'app-temperature-hero',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="temperature-hero" [attr.data-feeling]="feeling()">
      <p class="temperature-hero__city">{{ city() }}</p>
      <div class="temperature-hero__main">
        <span class="temperature-hero__glyph" aria-hidden="true">{{ glyph() }}</span>
        <div class="temperature-hero__copy">
          <p class="temperature-hero__temp">
            {{ value() }}<span class="temperature-hero__unit">°C</span>
          </p>
          <p class="temperature-hero__description">{{ description() }}</p>
          <p class="temperature-hero__feeling">sensação {{ feeling() }}</p>
        </div>
      </div>
    </div>
  `,
  styles: `
    .temperature-hero {
      display: grid;
      gap: 12px;
      padding: 16px 18px;
      border-radius: 16px;
      color: #0f172a;
      background: linear-gradient(135deg, #e0f2fe 0%, #f8fafc 70%);
    }

    .temperature-hero__city {
      margin: 0;
      font-size: 1.05rem;
      font-weight: 650;
      color: #0f172a;
    }

    .temperature-hero__main {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .temperature-hero[data-feeling='frio'] {
      background: linear-gradient(135deg, #dbeafe 0%, #f1f5f9 70%);
    }

    .temperature-hero[data-feeling='quente'] {
      background: linear-gradient(135deg, #ffedd5 0%, #fff7ed 70%);
    }

    .temperature-hero__glyph {
      font-size: 2.5rem;
      line-height: 1;
    }

    .temperature-hero__copy {
      display: grid;
      gap: 2px;
      min-width: 0;
    }

    .temperature-hero__temp {
      margin: 0;
      font-size: 2.25rem;
      font-weight: 650;
      letter-spacing: -0.04em;
      line-height: 1;
    }

    .temperature-hero__unit {
      margin-left: 2px;
      font-size: 1.1rem;
      font-weight: 600;
      color: #475569;
    }

    .temperature-hero__description {
      margin: 4px 0 0;
      font-size: 0.95rem;
      color: #334155;
    }

    .temperature-hero__feeling {
      margin: 0;
      font-size: 0.75rem;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: #64748b;
    }
  `,
})
export class TemperatureHeroComponent extends CatalogComponent<typeof temperatureHeroApi> {
  readonly city = computed(() => String(this.props().city.value() ?? ''));

  readonly value = computed(() => Math.round(this.props().temperature.value()));

  readonly description = computed(() => String(this.props().description.value() ?? ''));

  readonly feeling = computed(() => temperatureFeeling(this.value()));

  readonly glyph = computed(() => weatherGlyph(this.description(), this.value()));
}

export const temperatureHeroEntry: AngularComponentImplementation = {
  name: 'TemperatureHero',
  schema: temperatureHeroSchema,
  component: TemperatureHeroComponent,
};
