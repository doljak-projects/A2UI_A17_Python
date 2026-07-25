from __future__ import annotations

from typing import Any

from app.tools.base import Tool
from app.tools.registry import registry


class EchoTool(Tool):
    """Tool de exemplo que ecoa a mensagem recebida (útil para testar tool calling)."""

    name = "echo"
    description = "Retorna de volta a mensagem recebida."
    input_schema = {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "Mensagem a ser ecoada de volta",
            }
        },
        "required": ["message"],
        "additionalProperties": False,
    }

    def execute(self, arguments: dict[str, Any]) -> Any:
        return {"message": arguments["message"]}


def register_builtin_tools() -> None:
    """Registra as tools embutidas no registry padrão (idempotente)."""
    if "echo" not in registry:
        registry.register(EchoTool())
