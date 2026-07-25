from __future__ import annotations

import json
from typing import Any

from app.llm.types import LLMResponse, Message, ToolCall

Provider = str

OPENAI = "openai"
ANTHROPIC = "anthropic"


class UnsupportedProviderError(ValueError):
    """Levantada quando o provedor informado não é suportado."""


def _ensure_provider(provider: Provider) -> None:
    if provider not in (OPENAI, ANTHROPIC):
        raise UnsupportedProviderError(f"Provedor '{provider}' não suportado")


def build_tools_payload(
    provider: Provider, tools_schema: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Converte os schemas do `ToolRegistry` para o formato de tools do provedor."""
    _ensure_provider(provider)

    if provider == ANTHROPIC:
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["input_schema"],
            }
            for tool in tools_schema
        ]

    return [
        {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"],
            },
        }
        for tool in tools_schema
    ]


def build_messages_payload(
    provider: Provider, messages: list[Message]
) -> list[dict[str, Any]]:
    """Converte as mensagens internas para o formato de mensagens do provedor."""
    _ensure_provider(provider)
    builder = _anthropic_message if provider == ANTHROPIC else _openai_messages

    payload: list[dict[str, Any]] = []
    for message in messages:
        built = builder(message)
        payload.extend(built if isinstance(built, list) else [built])
    return payload


def _openai_messages(message: Message) -> list[dict[str, Any]]:
    if message.role == "tool":
        return [
            {
                "role": "tool",
                "tool_call_id": result.tool_call_id,
                "content": _as_text(result.content),
            }
            for result in message.tool_results
        ]

    entry: dict[str, Any] = {"role": message.role, "content": message.content}
    if message.tool_calls:
        entry["tool_calls"] = [
            {
                "id": call.id,
                "type": "function",
                "function": {
                    "name": call.name,
                    "arguments": json.dumps(call.arguments, ensure_ascii=False),
                },
            }
            for call in message.tool_calls
        ]
    return [entry]


def _anthropic_message(message: Message) -> dict[str, Any]:
    if message.role == "tool":
        return {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": result.tool_call_id,
                    "content": _as_text(result.content),
                    **({"is_error": True} if result.is_error else {}),
                }
                for result in message.tool_results
            ],
        }

    if message.tool_calls:
        content: list[dict[str, Any]] = []
        if message.content:
            content.append({"type": "text", "text": message.content})
        content.extend(
            {
                "type": "tool_use",
                "id": call.id,
                "name": call.name,
                "input": call.arguments,
            }
            for call in message.tool_calls
        )
        return {"role": message.role, "content": content}

    return {"role": message.role, "content": message.content}


def parse_response(provider: Provider, raw: dict[str, Any]) -> LLMResponse:
    """Normaliza a resposta bruta do provedor, extraindo texto e pedidos de tool."""
    _ensure_provider(provider)
    if provider == ANTHROPIC:
        return _parse_anthropic(raw)
    return _parse_openai(raw)


def _parse_openai(raw: dict[str, Any]) -> LLMResponse:
    choice = (raw.get("choices") or [{}])[0]
    message = choice.get("message") or {}

    tool_calls = [
        ToolCall(
            id=call.get("id", ""),
            name=call["function"]["name"],
            arguments=_loads(call["function"].get("arguments")),
        )
        for call in message.get("tool_calls") or []
    ]

    return LLMResponse(
        text=message.get("content"),
        tool_calls=tool_calls,
        stop_reason=choice.get("finish_reason"),
        raw=raw,
    )


def _parse_anthropic(raw: dict[str, Any]) -> LLMResponse:
    texts: list[str] = []
    tool_calls: list[ToolCall] = []

    for block in raw.get("content") or []:
        if block.get("type") == "text":
            texts.append(block.get("text", ""))
        elif block.get("type") == "tool_use":
            tool_calls.append(
                ToolCall(
                    id=block.get("id", ""),
                    name=block.get("name", ""),
                    arguments=block.get("input") or {},
                )
            )

    return LLMResponse(
        text="".join(texts) or None,
        tool_calls=tool_calls,
        stop_reason=raw.get("stop_reason"),
        raw=raw,
    )


def _loads(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not value:
        return {}
    return json.loads(value)


def _as_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    return json.dumps(content, ensure_ascii=False)
