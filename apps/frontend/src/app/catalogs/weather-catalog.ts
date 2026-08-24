import { BasicCatalogBase } from '@a2ui/angular/v0_9';

import { humidityGaugeEntry } from '../components/humidity-gauge/humidity-gauge.component';
import { temperatureHeroEntry } from '../components/temperature-hero/temperature-hero.component';

/** Mesmo id usado no backend (`app/agui/a2ui_constants.py`). */
export const WEATHER_CATALOG_ID =
  'https://a2ui.org/specification/v0_9/catalogs/weather/catalog.json';

export class WeatherCatalog extends BasicCatalogBase {
  constructor() {
    super({
      id: WEATHER_CATALOG_ID,
      extraComponents: [humidityGaugeEntry, temperatureHeroEntry],
    });
  }
}
