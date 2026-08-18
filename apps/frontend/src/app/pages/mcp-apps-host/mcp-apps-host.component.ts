import {
  AfterViewInit,
  Component,
  ElementRef,
  ViewChild,
  signal,
} from '@angular/core';
import { AppBridge, PostMessageTransport } from '@modelcontextprotocol/ext-apps/app-bridge';

import { environment } from '../../../environments/environment';
import { buildMockWeatherResult } from '../../core/services/weather-tool-for-a2ui';

/**
 * Demo isolada das issues #82/#83: host mínimo com iframe + AppBridge e dados
 * mockados de `get_weather`, sem CopilotKit.
 */
@Component({
  selector: 'app-mcp-apps-host',
  templateUrl: './mcp-apps-host.component.html',
  styleUrl: './mcp-apps-host.component.scss',
})
export class McpAppsHostComponent implements AfterViewInit {
  readonly status = signal('Carregando widget MCP Apps…');
  readonly error = signal<string | null>(null);

  private bridge?: AppBridge;

  @ViewChild('appFrame') private appFrame?: ElementRef<HTMLIFrameElement>;

  ngAfterViewInit(): void {
    void this.bootstrapHost();
  }

  private async bootstrapHost(): Promise<void> {
    const iframe = this.appFrame?.nativeElement;
    if (!iframe) return;

    iframe.src = `${environment.apiBaseUrl}/mcp-apps/weather-card`;

    iframe.onload = () => {
      void this.connectBridge(iframe);
    };
  }

  private async connectBridge(iframe: HTMLIFrameElement): Promise<void> {
    try {
      const contentWindow = iframe.contentWindow;
      if (!contentWindow) {
        throw new Error('Iframe sem contentWindow disponível.');
      }

      this.bridge = new AppBridge(
        null,
        { name: 'A2UI MCP Apps Host', version: '1.0.0' },
        { openLinks: {}, serverTools: {}, logging: {} },
        {
          hostContext: {
            theme: 'light',
            platform: 'web',
            displayMode: 'inline',
          },
        },
      );

      this.bridge.addEventListener('initialized', () => {
        this.status.set('Widget inicializado — enviando input/resultado mockados…');
        void this.bridge?.sendToolInput({ arguments: { city: 'São Paulo' } });
        void this.bridge?.sendToolResult({
          content: [
            {
              type: 'text',
              text: JSON.stringify(buildMockWeatherResult('São Paulo')),
            },
          ],
          structuredContent: buildMockWeatherResult('São Paulo'),
        });
      });

      this.bridge.onsizechange = (params) => {
        const height = params?.height;
        if (height && height > 0) {
          iframe.style.height = `${Math.ceil(height)}px`;
        }
      };

      const transport = new PostMessageTransport(contentWindow, contentWindow);
      await this.bridge.connect(transport);
      this.status.set('Host conectado ao widget via postMessage.');
    } catch (err) {
      this.error.set(err instanceof Error ? err.message : 'Falha ao conectar AppBridge');
    }
  }
}
