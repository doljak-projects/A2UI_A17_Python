from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Role = Literal["system", "user", "assistant", "tool"]


@dataclass(frozen=True)
class ToolCall:
    """Pedido do LLM para executar uma tool."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class ToolResult:
    """Resultado da execução de uma tool, devolvido ao LLM na rodada seguinte."""

    tool_call_id: str
    name: str
    content: Any
    is_error: bool = False


@dataclass
class Message:
    """Mensagem de uma conversa, no formato interno (agnóstico de provedor)."""

    role: Role
    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_results: list[ToolResult] = field(default_factory=list)


@dataclass
class LLMResponse:
    """Resposta normalizada do LLM."""

    text: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    stop_reason: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def requires_tool_execution(self) -> bool:
        return bool(self.tool_calls)
