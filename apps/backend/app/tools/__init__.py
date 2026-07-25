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
from app.tools.weather import GetWeatherTool, register_weather_tools

# Registra as tools embutidas ao importar o pacote.
register_builtin_tools()
register_weather_tools()

__all__ = [
    "Tool",
    "ToolRegistry",
    "ToolNotFoundError",
    "ToolAlreadyRegisteredError",
    "GetWeatherTool",
    "registry",
    "get_tools_schema",
    "execute_tool",
    "register_builtin_tools",
    "register_weather_tools",
]
