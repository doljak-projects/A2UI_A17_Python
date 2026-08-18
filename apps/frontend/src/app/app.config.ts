import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideCopilotKit } from '@copilotkit/angular';
import { BasicCatalog, provideA2Ui, provideMarkdownRenderer } from '@a2ui/angular/v0_9';

import { routes } from './app.routes';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { a2uiActivityRendererConfig } from './components/a2ui-activity-renderer/a2ui-activity-renderer.component';
import { WeatherCatalog } from './catalogs/weather-catalog';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideAnimationsAsync(),
    provideCopilotKit({
      defaultToolRendering: true,
      renderActivityMessages: [a2uiActivityRendererConfig],
    }),
    provideA2Ui({ catalogs: [new BasicCatalog(), new WeatherCatalog()] }),
    provideMarkdownRenderer(),
  ],
};
