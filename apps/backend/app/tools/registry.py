from __future__ import annotations

from typing import Any

from app.tools.base import Tool


class ToolNotFoundError(KeyError):
    """Levantada quando uma tool solicitada não está registrada."""


class ToolAlreadyRegisteredError(ValueError):
    """Levantada ao registrar uma tool com nome já existente."""


class ToolRegistry:
    """Registro central de tools: registra, descobre e executa de forma uniforme."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def __contains__(self, name: object) -> bool:
        return name in self._tools

    def __len__(self) -> int:
        return len(self._tools)

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ToolAlreadyRegisteredError(f"Tool '{tool.name}' já registrada")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolNotFoundError(f"Tool '{name}' não encontrada") from exc

    def list_tools(self) -> list[Tool]:
        return list(self._tools.values())

    def get_tools_schema(self) -> list[dict[str, Any]]:
        """Lista de schemas das tools para montar o payload ao LLM."""
        return [tool.schema() for tool in self._tools.values()]

    def execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Dispatcher: executa a tool registrada pelo nome."""
        return self.get(name).execute(arguments)


# Registry padrão da aplicação.
registry = ToolRegistry()


def get_tools_schema() -> list[dict[str, Any]]:
    return registry.get_tools_schema()


def execute_tool(name: str, arguments: dict[str, Any]) -> Any:
    return registry.execute_tool(name, arguments)
