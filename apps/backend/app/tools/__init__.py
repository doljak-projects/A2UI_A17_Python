from app.tools.base import Tool
from app.tools.examples import register_builtin_tools
from app.tools.registry import (
    ToolAlreadyRegisteredError,
    ToolNotFoundError,
    ToolRegistry,
    execute_tool,
    get_tools_schema,
    registry,
)

# Registra as tools embutidas ao importar o pacote.
register_builtin_tools()

__all__ = [
    "Tool",
    "ToolRegistry",
    "ToolNotFoundError",
    "ToolAlreadyRegisteredError",
    "registry",
    "get_tools_schema",
    "execute_tool",
    "register_builtin_tools",
]
