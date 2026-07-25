from __future__ import annotations

from dataclasses import dataclass, field

from app.llm.client import LLMClient, build_tools_for_client
from app.llm.types import LLMResponse, Message, ToolCall, ToolResult
from app.tools.registry import ToolRegistry, registry as default_registry

DEFAULT_MAX_ROUNDS = 5


class MaxToolRoundsExceededError(RuntimeError):
    """Levantada quando o LLM excede o limite de rodadas de tool calling."""


@dataclass
class ToolCallingResult:
    """Resultado final do loop, com a conversa completa para auditoria."""

    text: str | None
    messages: list[Message]
    rounds: int
    tool_results: list[ToolResult] = field(default_factory=list)


def execute_tool_calls(
    tool_calls: list[ToolCall], registry: ToolRegistry
) -> list[ToolResult]:
    """Executa as tools pedidas pelo LLM, capturando erros como resultado de tool."""
    results: list[ToolResult] = []
    for call in tool_calls:
        try:
            output = registry.execute_tool(call.name, call.arguments)
            results.append(ToolResult(call.id, call.name, output))
        except Exception as exc:  # devolvido ao LLM para que ele possa se corrigir
            results.append(ToolResult(call.id, call.name, str(exc), is_error=True))
    return results


def run_tool_calling(
    client: LLMClient,
    messages: list[Message],
    registry: ToolRegistry | None = None,
    max_rounds: int = DEFAULT_MAX_ROUNDS,
) -> ToolCallingResult:
    """Roda a conversa até o LLM responder sem pedir tools.

    A cada rodada: envia a conversa com as tools disponíveis, e se o LLM pedir
    execução de tools, executa-as e devolve os resultados na rodada seguinte.
    """
    registry = registry or default_registry
    tools = build_tools_for_client(client, registry.get_tools_schema())

    conversation = list(messages)
    all_results: list[ToolResult] = []

    for round_number in range(1, max_rounds + 1):
        response: LLMResponse = client.send(conversation, tools)

        if not response.requires_tool_execution:
            return ToolCallingResult(
                text=response.text,
                messages=conversation,
                rounds=round_number,
                tool_results=all_results,
            )

        conversation.append(
            Message(
                role="assistant",
                content=response.text,
                tool_calls=response.tool_calls,
            )
        )

        results = execute_tool_calls(response.tool_calls, registry)
        all_results.extend(results)
        conversation.append(Message(role="tool", tool_results=results))

    raise MaxToolRoundsExceededError(
        f"LLM excedeu o limite de {max_rounds} rodadas de tool calling"
    )
