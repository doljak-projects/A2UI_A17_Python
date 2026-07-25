import json

import pytest

from app.llm.providers import (
    ANTHROPIC,
    OPENAI,
    UnsupportedProviderError,
    build_messages_payload,
    build_tools_payload,
    parse_response,
)
from app.llm.types import Message, ToolCall, ToolResult

TOOLS_SCHEMA = [
    {
        "name": "echo",
        "description": "Retorna de volta a mensagem recebida.",
        "input_schema": {
            "type": "object",
            "properties": {"message": {"type": "string"}},
            "required": ["message"],
        },
    }
]


def test_build_tools_payload_openai():
    payload = build_tools_payload(OPENAI, TOOLS_SCHEMA)
    assert payload == [
        {
            "type": "function",
            "function": {
                "name": "echo",
                "description": "Retorna de volta a mensagem recebida.",
                "parameters": TOOLS_SCHEMA[0]["input_schema"],
            },
        }
    ]


def test_build_tools_payload_anthropic():
    payload = build_tools_payload(ANTHROPIC, TOOLS_SCHEMA)
    assert payload == [
        {
            "name": "echo",
            "description": "Retorna de volta a mensagem recebida.",
            "input_schema": TOOLS_SCHEMA[0]["input_schema"],
        }
    ]


def test_unsupported_provider_raises():
    with pytest.raises(UnsupportedProviderError):
        build_tools_payload("gemini", TOOLS_SCHEMA)


def test_build_messages_payload_openai_with_tool_cycle():
    messages = [
        Message(role="user", content="ecoa oi"),
        Message(
            role="assistant",
            content=None,
            tool_calls=[ToolCall(id="call_1", name="echo", arguments={"message": "oi"})],
        ),
        Message(
            role="tool",
            tool_results=[ToolResult("call_1", "echo", {"message": "oi"})],
        ),
    ]

    payload = build_messages_payload(OPENAI, messages)

    assert payload[0] == {"role": "user", "content": "ecoa oi"}
    assert payload[1]["tool_calls"][0]["id"] == "call_1"
    assert json.loads(payload[1]["tool_calls"][0]["function"]["arguments"]) == {
        "message": "oi"
    }
    assert payload[2] == {
        "role": "tool",
        "tool_call_id": "call_1",
        "content": '{"message": "oi"}',
    }


def test_build_messages_payload_anthropic_with_tool_cycle():
    messages = [
        Message(role="user", content="ecoa oi"),
        Message(
            role="assistant",
            tool_calls=[ToolCall(id="tu_1", name="echo", arguments={"message": "oi"})],
        ),
        Message(
            role="tool",
            tool_results=[ToolResult("tu_1", "echo", {"message": "oi"})],
        ),
    ]

    payload = build_messages_payload(ANTHROPIC, messages)

    assert payload[1]["content"][0] == {
        "type": "tool_use",
        "id": "tu_1",
        "name": "echo",
        "input": {"message": "oi"},
    }
    assert payload[2]["role"] == "user"
    assert payload[2]["content"][0]["type"] == "tool_result"
    assert payload[2]["content"][0]["tool_use_id"] == "tu_1"


def test_parse_response_openai_tool_call():
    raw = {
        "choices": [
            {
                "finish_reason": "tool_calls",
                "message": {
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_1",
                            "type": "function",
                            "function": {
                                "name": "echo",
                                "arguments": '{"message": "oi"}',
                            },
                        }
                    ],
                },
            }
        ]
    }

    response = parse_response(OPENAI, raw)

    assert response.requires_tool_execution
    assert response.tool_calls[0] == ToolCall("call_1", "echo", {"message": "oi"})
    assert response.stop_reason == "tool_calls"


def test_parse_response_anthropic_text_and_tool_use():
    raw = {
        "stop_reason": "tool_use",
        "content": [
            {"type": "text", "text": "vou ecoar"},
            {"type": "tool_use", "id": "tu_1", "name": "echo", "input": {"message": "oi"}},
        ],
    }

    response = parse_response(ANTHROPIC, raw)

    assert response.text == "vou ecoar"
    assert response.tool_calls[0] == ToolCall("tu_1", "echo", {"message": "oi"})


def test_parse_response_without_tool_calls():
    raw = {"choices": [{"finish_reason": "stop", "message": {"content": "pronto"}}]}
    response = parse_response(OPENAI, raw)

    assert response.text == "pronto"
    assert not response.requires_tool_execution
