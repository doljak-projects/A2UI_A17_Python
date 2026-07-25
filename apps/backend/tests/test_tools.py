import pytest

from app.tools import execute_tool, get_tools_schema, registry
from app.tools.base import Tool
from app.tools.registry import (
    ToolAlreadyRegisteredError,
    ToolNotFoundError,
    ToolRegistry,
)


class _AddTool(Tool):
    name = "add"
    description = "Soma dois números."
    input_schema = {
        "type": "object",
        "properties": {
            "a": {"type": "number"},
            "b": {"type": "number"},
        },
        "required": ["a", "b"],
    }

    def execute(self, arguments):
        return arguments["a"] + arguments["b"]


def test_register_and_execute():
    reg = ToolRegistry()
    reg.register(_AddTool())

    assert "add" in reg
    assert len(reg) == 1
    assert reg.execute_tool("add", {"a": 2, "b": 3}) == 5


def test_get_tools_schema_shape():
    reg = ToolRegistry()
    reg.register(_AddTool())

    schema = reg.get_tools_schema()
    assert schema == [
        {
            "name": "add",
            "description": "Soma dois números.",
            "input_schema": _AddTool.input_schema,
        }
    ]


def test_duplicate_registration_raises():
    reg = ToolRegistry()
    reg.register(_AddTool())
    with pytest.raises(ToolAlreadyRegisteredError):
        reg.register(_AddTool())


def test_unknown_tool_raises():
    reg = ToolRegistry()
    with pytest.raises(ToolNotFoundError):
        reg.execute_tool("missing", {})


def test_builtin_echo_registered_in_default_registry():
    assert "echo" in registry
    result = execute_tool("echo", {"message": "olá"})
    assert result == {"message": "olá"}
    names = [t["name"] for t in get_tools_schema()]
    assert "echo" in names
