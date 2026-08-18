from __future__ import annotations

import anyio
import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from app.agui.a2ui_constants import WEATHER_MCP_RESOURCE_URI
from app.mcp.resources import load_weather_app_html, read_weather_app_resource
from app.mcp.server import build_mcp_server


def test_load_weather_app_html_returns_widget_markup():
    html = load_weather_app_html()

    assert "<html" in html
    assert "Weather MCP App" in html


def test_read_weather_app_resource_matches_known_uri():
    resource = read_weather_app_resource(WEATHER_MCP_RESOURCE_URI)

    assert resource["uri"] == WEATHER_MCP_RESOURCE_URI
    assert resource["mimeType"] == "text/html"
    assert "Weather MCP App" in resource["text"]


def test_read_weather_app_resource_rejects_unknown_uri():
    with pytest.raises(KeyError):
        read_weather_app_resource("ui://unknown/resource.html")


def test_mcp_server_exposes_get_weather_ui_metadata_and_resource():
    """Exercita o servidor MCP real (sessão in-memory, mesmo padrão de
    `test_mcp_server.py`) — não só as funções Python isoladas — pra confirmar
    que `get_weather` anuncia `meta.ui.resourceUri` e que o recurso é
    listado/lido via protocolo (issue #81)."""

    async def main() -> tuple[dict[str, object], list[str], str]:
        async with create_connected_server_and_client_session(build_mcp_server()) as client:
            tools = (await client.list_tools()).tools
            weather_tool = next(tool for tool in tools if tool.name == "get_weather")

            resources = (await client.list_resources()).resources
            resource_uris = [str(resource.uri) for resource in resources]

            read_result = await client.read_resource(WEATHER_MCP_RESOURCE_URI)
            html = read_result.contents[0].text

            return weather_tool.model_dump(by_alias=True, exclude_none=True), resource_uris, html

    tool_dump, resource_uris, html = anyio.run(main)

    assert tool_dump.get("meta", {}).get("ui", {}).get("resourceUri") == WEATHER_MCP_RESOURCE_URI
    assert WEATHER_MCP_RESOURCE_URI in resource_uris
    assert "Weather MCP App" in html
