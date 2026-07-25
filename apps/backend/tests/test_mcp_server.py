from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

import anyio
from fastapi.testclient import TestClient
from mcp.client.session import ClientSession
from mcp.shared.memory import create_connected_server_and_client_session

from app.core.config import settings
from app.main import create_app
from app.mcp.server import MCP_PATH, build_mcp_server
from app.tools.base import Tool
from app.tools.registry import ToolRegistry

INITIALIZE_REQUEST = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "test-client", "version": "1.0"},
    },
}


class _GreetTool(Tool):
    name = "greet"
    description = "Saúda alguém pelo nome."
    input_schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
        "additionalProperties": False,
    }

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def execute(self, arguments: dict[str, Any]) -> Any:
        self.calls.append(arguments)
        return {"greeting": f"olá, {arguments['name']}"}


class _CountTool(Tool):
    name = "count"
    description = "Conta os caracteres de um texto."
    input_schema = {
        "type": "object",
        "properties": {"text": {"type": "string"}},
        "required": ["text"],
    }

    def execute(self, arguments: dict[str, Any]) -> Any:
        return len(arguments["text"])


class _BoomTool(Tool):
    name = "boom"
    description = "Sempre falha."
    input_schema = {"type": "object", "properties": {}}

    def execute(self, arguments: dict[str, Any]) -> Any:
        raise RuntimeError("falhou de propósito")


def _with_client(
    registry: ToolRegistry, scenario: Callable[[ClientSession], Awaitable[Any]]
) -> Any:
    """Roda `scenario` contra um cliente MCP in-memory ligado ao servidor do registry.

    Usa o transporte in-memory do SDK em vez de mocks, então o caminho exercitado
    é o mesmo protocolo que um cliente externo fala.
    """

    async def main() -> Any:
        async with create_connected_server_and_client_session(build_mcp_server(registry)) as client:
            return await scenario(client)

    return anyio.run(main)


def test_lists_tools_declared_in_the_registry():
    registry = ToolRegistry()
    registry.register(_GreetTool())
    registry.register(_CountTool())

    result = _with_client(registry, lambda client: client.list_tools())

    listed = {tool.name: tool for tool in result.tools}
    assert set(listed) == {"greet", "count"}
    assert listed["greet"].description == "Saúda alguém pelo nome."
    assert listed["greet"].inputSchema == _GreetTool.input_schema
    assert listed["count"].inputSchema == _CountTool.input_schema


def test_tool_registered_after_the_server_started_is_listed():
    registry = ToolRegistry()
    registry.register(_GreetTool())

    async def scenario(client: ClientSession) -> tuple[list[str], list[str]]:
        before = [tool.name for tool in (await client.list_tools()).tools]
        registry.register(_CountTool())
        after = [tool.name for tool in (await client.list_tools()).tools]
        return before, after

    before, after = _with_client(registry, scenario)

    assert before == ["greet"]
    assert after == ["greet", "count"]


def test_calling_a_tool_executes_the_registry_tool():
    registry = ToolRegistry()
    greet = _GreetTool()
    registry.register(greet)

    result = _with_client(registry, lambda client: client.call_tool("greet", {"name": "Ana"}))

    assert result.isError is False
    assert result.structuredContent == {"greeting": "olá, Ana"}
    assert greet.calls == [{"name": "Ana"}]


def test_non_dict_result_is_returned_as_text_content():
    registry = ToolRegistry()
    registry.register(_CountTool())

    result = _with_client(registry, lambda client: client.call_tool("count", {"text": "abcd"}))

    assert result.isError is False
    assert result.content[0].text == "4"


def test_calling_an_unknown_tool_reports_an_error():
    registry = ToolRegistry()
    registry.register(_GreetTool())

    result = _with_client(registry, lambda client: client.call_tool("inexistente", {}))

    assert result.isError is True
    assert "inexistente" in result.content[0].text


def test_invalid_arguments_are_rejected_before_execution():
    registry = ToolRegistry()
    greet = _GreetTool()
    registry.register(greet)

    result = _with_client(registry, lambda client: client.call_tool("greet", {}))

    assert result.isError is True
    assert greet.calls == []


def test_tool_failure_is_reported_as_an_error_result():
    registry = ToolRegistry()
    registry.register(_BoomTool())

    result = _with_client(registry, lambda client: client.call_tool("boom", {}))

    assert result.isError is True
    assert "falhou de propósito" in result.content[0].text


def test_builtin_tools_are_exposed_by_the_default_registry():
    async def main() -> list[str]:
        async with create_connected_server_and_client_session(build_mcp_server()) as client:
            return [tool.name for tool in (await client.list_tools()).tools]

    names = anyio.run(main)

    assert "echo" in names
    assert "get_weather" in names


def test_listing_tools_does_not_require_the_weather_api_key(monkeypatch):
    # Registrar/listar não pode exigir a chave: só a execução da tool depende dela.
    monkeypatch.setattr(settings, "weather_api_key", None)

    async def main() -> list[str]:
        async with create_connected_server_and_client_session(build_mcp_server()) as client:
            return [tool.name for tool in (await client.list_tools()).tools]

    assert "get_weather" in anyio.run(main)


def test_mcp_endpoint_is_served_alongside_the_rest_api():
    app = create_app()

    with TestClient(app) as client:
        assert client.get("/api/health").status_code == 200
        response = client.post(
            MCP_PATH,
            json=INITIALIZE_REQUEST,
            headers={
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json",
            },
        )

    # Sessão criada indica que o session manager subiu junto com o lifespan da app.
    assert response.status_code == 200
    assert response.headers["mcp-session-id"]
    assert settings.app_name in response.text
