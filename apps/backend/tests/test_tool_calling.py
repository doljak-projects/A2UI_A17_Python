import pytest

from app.llm.tool_calling import (
    MaxToolRoundsExceededError,
    execute_tool_calls,
    run_tool_calling,
)
from app.llm.types import LLMResponse, Message, ToolCall
from app.tools import registry


class FakeLLMClient:
    """Cliente falso que devolve respostas pré-programadas e grava as chamadas."""

    def __init__(self, responses, provider="openai"):
        self.provider = provider
        self._responses = list(responses)
        self.calls = []

    def send(self, messages, tools=None):
        self.calls.append({"messages": list(messages), "tools": tools})
        return self._responses.pop(0)


def test_run_tool_calling_executes_echo_and_returns_final_answer():
    client = FakeLLMClient(
        [
            LLMResponse(
                tool_calls=[ToolCall("call_1", "echo", {"message": "oi"})],
                stop_reason="tool_calls",
            ),
            LLMResponse(text="O eco foi: oi", stop_reason="stop"),
        ]
    )

    result = run_tool_calling(client, [Message(role="user", content="ecoa oi")])

    assert result.text == "O eco foi: oi"
    assert result.rounds == 2
    assert result.tool_results[0].content == {"message": "oi"}
    assert result.tool_results[0].is_error is False


def test_tools_payload_is_sent_to_the_llm():
    client = FakeLLMClient([LLMResponse(text="pronto", stop_reason="stop")])

    run_tool_calling(client, [Message(role="user", content="oi")])

    tools = client.calls[0]["tools"]
    names = [tool["function"]["name"] for tool in tools]
    assert "echo" in names


def test_conversation_carries_tool_result_to_next_round():
    client = FakeLLMClient(
        [
            LLMResponse(tool_calls=[ToolCall("call_1", "echo", {"message": "oi"})]),
            LLMResponse(text="fim"),
        ]
    )

    run_tool_calling(client, [Message(role="user", content="ecoa oi")])

    second_round = client.calls[1]["messages"]
    assert second_round[1].tool_calls[0].name == "echo"
    assert second_round[2].role == "tool"
    assert second_round[2].tool_results[0].tool_call_id == "call_1"


def test_tool_error_is_returned_to_the_llm_instead_of_raising():
    results = execute_tool_calls([ToolCall("call_1", "missing", {})], registry)

    assert results[0].is_error is True
    assert "missing" in results[0].content


def test_max_rounds_exceeded():
    looping = [
        LLMResponse(tool_calls=[ToolCall(f"call_{i}", "echo", {"message": "x"})])
        for i in range(3)
    ]
    client = FakeLLMClient(looping)

    with pytest.raises(MaxToolRoundsExceededError):
        run_tool_calling(client, [Message(role="user", content="loop")], max_rounds=3)
