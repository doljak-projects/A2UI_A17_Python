from __future__ import annotations

import json
from functools import partial
from typing import Any

from anyio.to_thread import run_sync
from fastapi import FastAPI
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.types import ContentBlock, Resource, TextContent
from mcp.types import Tool as McpTool
from starlette.routing import Route
from starlette.types import Receive, Scope, Send

import app.tools  # noqa: F401  (import pelo efeito de registrar as tools embutidas)
from app.agui.a2ui_constants import WEATHER_MCP_RESOURCE_URI
from app.core.config import settings
from app.mcp.resources import read_weather_app_resource
from app.tools.registry import ToolRegistry
from app.tools.registry import registry as default_registry

# Rota do transporte Streamable HTTP: clientes MCP apontam para <base_url>/mcp.
MCP_PATH = "/mcp"


def build_mcp_server(registry: ToolRegistry | None = None) -> Server[object, Any]:
    """Servidor MCP que espelha o `ToolRegistry` em vez de redeclarar as tools.

    Recebe o registry por parâmetro para permitir testar com um registry isolado.
    """
    tools = default_registry if registry is None else registry
    server: Server[object, Any] = Server(name=settings.app_name, version=settings.version)

    @server.list_tools()
    async def list_tools() -> list[McpTool]:
        # Consultado a cada `tools/list`, então tools registradas depois do boot
        # aparecem sozinhas — nada de snapshot no momento da construção.
        return [
            McpTool(
                name=tool.name,
                description=tool.description,
                inputSchema=tool.input_schema,
                **(
                    {
                        "meta": {
                            "ui": {
                                "resourceUri": WEATHER_MCP_RESOURCE_URI,
                            },
                        },
                    }
                    if tool.name == "get_weather"
                    else {}
                ),
            )
            for tool in tools.list_tools()
        ]

    @server.list_resources()
    async def list_resources() -> list[Resource]:
        return [
            Resource(
                uri=WEATHER_MCP_RESOURCE_URI,
                name="Weather MCP App",
                description="Widget HTML interativo para o resultado de get_weather.",
                mimeType="text/html",
            )
        ]

    @server.read_resource()
    async def read_resource(uri: str) -> str:
        # O SDK MCP entrega `uri` como `pydantic.AnyUrl`, não `str` — apesar da
        # assinatura do decorator declarar `str`. `AnyUrl` não é igual a uma
        # `str` equivalente (`AnyUrl(...) == "..."` é `False`), então comparar
        # direto sempre falhava com "Recurso desconhecido" mesmo pro URI certo.
        resource = read_weather_app_resource(str(uri))
        return resource["text"]

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict[str, Any]
    ) -> dict[str, Any] | list[ContentBlock]:
        # `Tool.execute` é síncrono e faz I/O de rede (get_weather usa httpx.Client),
        # por isso vai para uma thread: no event loop travaria a app inteira.
        result = await run_sync(partial(tools.execute_tool, name, arguments))
        return _to_content(result)

    return server


def _to_content(result: Any) -> dict[str, Any] | list[ContentBlock]:
    """Adapta o retorno livre das tools ao que o `CallToolResult` aceita.

    Dict vira `structuredContent` (o SDK também gera o texto equivalente); os
    demais tipos viram texto, já que o protocolo não transporta valores soltos.
    """
    if isinstance(result, dict):
        return result
    if isinstance(result, str):
        return [TextContent(type="text", text=result)]
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, default=str))]


def build_session_manager(registry: ToolRegistry | None = None) -> StreamableHTTPSessionManager:
    """Session manager do transporte Streamable HTTP para o servidor MCP.

    A instância é de uso único: `run()` tem de ser chamado no lifespan da app,
    senão a primeira requisição em `/mcp` falha com "Task group is not initialized".
    """
    return StreamableHTTPSessionManager(app=build_mcp_server(registry))


class _StreamableHttpAsgiApp:
    """Adapta `handle_request` a um app ASGI.

    Precisa ser um objeto chamável, e não uma função: a `Route` do Starlette
    trataria função/método como endpoint HTTP comum e quebraria o streaming.
    """

    def __init__(self, session_manager: StreamableHTTPSessionManager) -> None:
        self._session_manager = session_manager

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self._session_manager.handle_request(scope, receive, send)


def add_mcp_route(app: FastAPI, session_manager: StreamableHTTPSessionManager) -> None:
    """Publica o endpoint MCP em `MCP_PATH`.

    Usa `Route` em vez de `app.mount()` para o path casar exatamente: um
    `Mount("/mcp")` só atenderia em `/mcp/` e devolveria redirect 307 aos
    clientes que falam com `/mcp`.
    """
    app.router.routes.append(
        Route(MCP_PATH, endpoint=_StreamableHttpAsgiApp(session_manager), include_in_schema=False)
    )
