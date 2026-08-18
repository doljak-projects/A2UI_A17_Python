import { Routes } from '@angular/router';
import { provideMCPApps } from '@copilotkit/angular/mcp-apps';

/**
 * Arquivo de rotas dedicado (em vez de `loadComponent` direto em
 * `app.routes.ts`) só pra isolar `provideMCPApps` (issue #86) num chunk lazy
 * próprio — `app.routes.ts` é importado de forma eager por `app.config.ts`,
 * então qualquer provider referenciado lá dentro (mesmo que só usado por uma
 * rota específica) entra no bundle inicial. Via `loadChildren`, este arquivo
 * só é buscado quando `/copilot-weather-chat` é navegado, levando o pacote
 * `@modelcontextprotocol/ext-apps` (dependência de `@copilotkit/angular/mcp-apps`)
 * junto pro chunk lazy — sem isso, o orçamento de bundle inicial (1.6 MB,
 * ajustado na issue #73) estourava de novo.
 */
export const COPILOT_WEATHER_CHAT_ROUTES: Routes = [
  {
    path: '',
    providers: [
      provideMCPApps({
        hostInfo: { name: 'A2UI Weather Chat', version: '1.0.0' },
        hostContext: { theme: 'light', platform: 'web', displayMode: 'inline' },
      }),
    ],
    loadComponent: () =>
      import('./copilot-weather-chat.component').then((m) => m.CopilotWeatherChatComponent),
  },
];
