import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideCopilotKit } from '@copilotkit/angular';
import { BasicCatalog, provideA2Ui, provideMarkdownRenderer } from '@a2ui/angular/v0_9';

import { routes } from './app.routes';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { a2uiActivityRendererConfig } from './components/a2ui-activity-renderer/a2ui-activity-renderer.component';
import { WeatherCatalog } from './catalogs/weather-catalog';

// `provideCopilotKit` precisa ficar na raiz: `CopilotKit` é `providedIn: 'root'`
// e injeta `COPILOT_KIT_CONFIG` no próprio construtor — um provider de rota
// (lazy) não é visível pra um singleton root, então isolar isso numa rota
// (como fizemos com `provideMCPApps`) quebra em runtime (`NG0201: No provider
// found for COPILOT_KIT_CONFIG`), mesmo compilando sem erro. Isso também
// significa que o `<copilot-chat>` pronto (issue de unificação da rota /chat)
// não pode ficar isolado num chunk lazy só dele — ver nota no doc da issue
// sobre o custo de bundle resultante.
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
