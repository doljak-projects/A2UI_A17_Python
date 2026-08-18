"""Constantes compartilhadas entre os módulos A2UI do backend."""

from __future__ import annotations

# Mesmo id padrão do `BasicCatalog` do SDK Angular (@a2ui/angular v0_9).
BASIC_CATALOG_ID = "https://a2ui.org/specification/v0_9/catalogs/basic/catalog.json"

# Mesmo id do `WeatherCatalog` (frontend, `catalogs/weather-catalog.ts`, issue #76).
WEATHER_CATALOG_ID = "https://a2ui.org/specification/v0_9/catalogs/weather/catalog.json"

A2UI_SURFACE_ACTIVITY_TYPE = "a2ui-surface"

REFRESH_WEATHER_ACTION = "refreshWeather"

# Resource URI do widget MCP Apps de clima (issues #81/#83), servido tanto
# pelo MCP Server (`app/mcp/server.py`) quanto por uma rota HTML direta
# (`app/api/routes/mcp_apps.py`) pra demos isoladas sem cliente MCP.
WEATHER_MCP_RESOURCE_URI = "ui://weather/card.html"
