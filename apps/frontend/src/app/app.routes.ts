import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'chat', pathMatch: 'full' },
  {
    path: 'chat',
    loadComponent: () =>
      import('./pages/copilot-weather-chat/copilot-weather-chat.component').then(
        (m) => m.CopilotWeatherChatComponent,
      ),
  },
  {
    path: 'home',
    loadComponent: () =>
      import('./pages/home/home.component').then((m) => m.HomeComponent),
  },
  {
    path: 'agui-test',
    loadComponent: () =>
      import('./pages/agui-test/agui-test.component').then((m) => m.AguiTestComponent),
  },
  {
    path: 'a2ui-test',
    loadComponent: () =>
      import('./pages/a2ui-test/a2ui-test.component').then((m) => m.A2uiTestComponent),
  },
  {
    path: 'mcp-apps-host',
    loadComponent: () =>
      import('./pages/mcp-apps-host/mcp-apps-host.component').then(
        (m) => m.McpAppsHostComponent,
      ),
  },
  { path: '**', redirectTo: 'chat' },
];
