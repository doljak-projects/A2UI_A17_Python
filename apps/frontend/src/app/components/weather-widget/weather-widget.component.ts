import { Component, computed, input } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AngularToolCall, ToolRenderer } from '@copilotkit/angular';
import { z } from 'zod/v4';

import { weatherToolArgsSchema } from '../../core/services/weather-frontend-tool';
import {
  WeatherToolResult,
  parseWeatherToolResult,
} from '../../core/services/weather-tool-for-a2ui';

type WeatherToolArgs = z.infer<typeof weatherToolArgsSchema>;

/**
 * Widget Angular anexado à frontend tool `show_weather` (issue #49).
 * Renderizado no histórico do chat via `<copilot-render-tool-calls>`.
 */
@Component({
  selector: 'app-weather-widget',
  imports: [MatCardModule, MatIconModule, MatProgressSpinnerModule],
  templateUrl: './weather-widget.component.html',
  styleUrl: './weather-widget.component.scss',
})
export class WeatherWidgetComponent implements ToolRenderer<WeatherToolArgs> {
  readonly toolCall = input.required<AngularToolCall<WeatherToolArgs>>();

  protected readonly city = computed(() => this.toolCall().args.city ?? '—');
  protected readonly isLoading = computed(() => this.toolCall().status !== 'complete');
  protected readonly weather = computed((): WeatherToolResult | null => {
    const call = this.toolCall();
    if (call.status !== 'complete' || !call.result) {
      return null;
    }

    return parseWeatherToolResult(call.result);
  });
}
