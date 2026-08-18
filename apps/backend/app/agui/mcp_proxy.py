"""Proxy manual de requisições MCP Apps para o registry/servidor interno (issue #85)."""

from __future__ import annotations

import json
from typing import Any

from app.agui.a2ui_constants import WEATHER_MCP_RESOURCE_URI
from app.mcp.resources import read_weather_app_resource
from app.tools.registry import registry


class McpProxyError(ValueError):
    """Erro de validação ou execução ao rotear uma requisição MCP proxied."""


def execute_proxied_mcp_request(request: dict[str, Any]) -> dict[str, Any]:
    """Atende `forwardedProps.__proxiedMCPRequest` emitido pelo CopilotKit MCP Apps."""
    method = request.get("method")
    params = request.get("params") or {}

    if method == "resources/read":
        uri = params.get("uri")
        if not uri:
            raise McpProxyError("resources/read requer params.uri")
        if uri != WEATHER_MCP_RESOURCE_URI:
            raise McpProxyError(f"Recurso MCP não suportado: {uri}")
        resource = read_weather_app_resource(uri)
        return {"contents": [resource]}

    if method == "tools/call":
        name = params.get("name")
        if not name:
            raise McpProxyError("tools/call requer params.name")
        arguments = params.get("arguments") or {}
        result = registry.execute_tool(name, arguments)
        if isinstance(result, dict):
            structured = result
            text = json.dumps(result, ensure_ascii=False)
        else:
            structured = None
            text = str(result)
        return {
            "content": [{"type": "text", "text": text}],
            "structuredContent": structured,
        }

    raise McpProxyError(f"Método MCP proxied não suportado: {method}")
