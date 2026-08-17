import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'chat', pathMatch: 'full' },
  {
    path: 'chat',
    loadComponent: () =>
      import('./pages/chat/chat.component').then((m) => m.ChatComponent),
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
    path: 'copilot-weather-chat',
    loadComponent: () =>
      import('./pages/copilot-weather-chat/copilot-weather-chat.component').then(
        (m) => m.CopilotWeatherChatComponent,
      ),
  },
  { path: '**', redirectTo: 'chat' },
];
