import json

import httpx
import pytest

from app.core.config import Settings
from app.llm.client import HttpLLMClient
from app.llm.sse import format_sse, iter_sse_json
from app.llm.streaming import (
    EVENT_DELTA,
    EVENT_DONE,
    EVENT_TOOL_CALL,
    EVENT_TOOL_RESULT,
    AnthropicStreamAccumulator,
    OpenAIStreamAccumulator,
    make_accumulator,
    stream_tool_calling,
)
from app.llm.tool_calling import MaxToolRoundsExceededError
from app.llm.types import Message
from app.tools.base import Tool
from app.tools.registry import ToolRegistry


class _EchoTool(Tool):
    name = "echo"
    description = "Ecoa a mensagem."
    input_schema = {
        "type": "object",
        "properties": {"message": {"type": "string"}},
        "required": ["message"],
    }

    def execute(self, arguments):
        return {"message": arguments["message"]}


class _FakeStreamingClient:
    """Cliente que devolve rodadas de chunks pré-definidas, uma por chamada."""

    def __init__(self, rounds, provider="openai"):
        self.provider = provider
        self._rounds = list(rounds)
        self.conversations = []

    def stream(self, messages, tools=None):
        self.conversations.append(list(messages))
        yield from self._rounds.pop(0)


def openai_text_chunk(text):
    return {"choices": [{"delta": {"content": text}}]}


def openai_tool_chunk(index, *, call_id=None, name=None, arguments=None):
    call = {"index": index}
    if call_id:
        call["id"] = call_id
    function = {}
    if name:
        function["name"] = name
    if arguments is not None:
        function["arguments"] = arguments
    if function:
        call["function"] = function
    return {"choices": [{"delta": {"tool_calls": [call]}}]}


def make_registry():
    registry = ToolRegistry()
    registry.register(_EchoTool())
    return registry


def test_iter_sse_json_skips_noise_and_stops_at_done():
    lines = [
        "event: message",
        'data: {"a": 1}',
        "",
        ": comentário",
        'data: {"b": 2}',
        "data: [DONE]",
        'data: {"nunca": true}',
    ]

    assert list(iter_sse_json(lines)) == [{"a": 1}, {"b": 2}]


def test_format_sse_frame():
    frame = format_sse("delta", {"text": "olá"})

    assert frame == 'event: delta\ndata: {"text": "olá"}\n\n'


def test_openai_accumulator_yields_text_and_builds_response():
    accumulator = OpenAIStreamAccumulator()

    deltas = [
        text
        for chunk in [openai_text_chunk("Olá"), openai_text_chunk(" mundo")]
        for text in accumulator.feed(chunk)
    ]

    assert deltas == ["Olá", " mundo"]
    assert accumulator.result().text == "Olá mundo"


def test_openai_accumulator_reassembles_fragmented_tool_call():
    accumulator = OpenAIStreamAccumulator()
    chunks = [
        openai_tool_chunk(0, call_id="call_1", name="get_weather", arguments=""),
        openai_tool_chunk(0, arguments='{"ci'),
        openai_tool_chunk(0, arguments='ty": "S'),
        openai_tool_chunk(0, arguments='ão Paulo"}'),
        {"choices": [{"delta": {}, "finish_reason": "tool_calls"}]},
    ]

    for chunk in chunks:
        assert list(accumulator.feed(chunk)) == []

    response = accumulator.result()
    assert response.stop_reason == "tool_calls"
    assert len(response.tool_calls) == 1
    call = response.tool_calls[0]
    assert (call.id, call.name, call.arguments) == (
        "call_1",
        "get_weather",
        {"city": "São Paulo"},
    )


def test_openai_accumulator_keeps_parallel_tool_calls_separate():
    accumulator = OpenAIStreamAccumulator()
    for chunk in [
        openai_tool_chunk(0, call_id="a", name="echo", arguments='{"message"'),
        openai_tool_chunk(1, call_id="b", name="echo", arguments='{"message"'),
        openai_tool_chunk(0, arguments=': "um"}'),
        openai_tool_chunk(1, arguments=': "dois"}'),
    ]:
        list(accumulator.feed(chunk))

    calls = accumulator.result().tool_calls
    assert [(c.id, c.arguments["message"]) for c in calls] == [("a", "um"), ("b", "dois")]


def test_anthropic_accumulator_handles_text_and_tool_use():
    accumulator = AnthropicStreamAccumulator()
    chunks = [
        {
            "type": "content_block_start",
            "index": 0,
            "content_block": {"type": "tool_use", "id": "toolu_1", "name": "get_weather"},
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "input_json_delta", "partial_json": '{"city":'},
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "input_json_delta", "partial_json": ' "Lisboa"}'},
        },
        {
            "type": "content_block_delta",
            "index": 1,
            "delta": {"type": "text_delta", "text": "Consultando"},
        },
        {"type": "message_delta", "delta": {"stop_reason": "tool_use"}},
    ]

    deltas = [text for chunk in chunks for text in accumulator.feed(chunk)]

    response = accumulator.result()
    assert deltas == ["Consultando"]
    assert response.stop_reason == "tool_use"
    assert response.tool_calls[0].arguments == {"city": "Lisboa"}


def test_make_accumulator_rejects_unknown_provider():
    with pytest.raises(Exception, match="não suportado"):
        make_accumulator("gemini")


def test_stream_tool_calling_emits_events_in_order():
    client = _FakeStreamingClient(
        rounds=[
            [
                openai_tool_chunk(0, call_id="call_1", name="echo", arguments='{"message": "oi"}'),
                {"choices": [{"delta": {}, "finish_reason": "tool_calls"}]},
            ],
            [openai_text_chunk("Você disse "), openai_text_chunk("oi")],
        ]
    )

    events = list(
        stream_tool_calling(client, [Message(role="user", content="diga oi")], make_registry())
    )

    assert [event.type for event in events] == [
        EVENT_TOOL_CALL,
        EVENT_TOOL_RESULT,
        EVENT_DELTA,
        EVENT_DELTA,
        EVENT_DONE,
    ]
    assert events[1].data == {
        "id": "call_1",
        "name": "echo",
        "content": {"message": "oi"},
        "is_error": False,
    }
    assert events[-1].data == {"text": "Você disse oi", "rounds": 2}


def test_stream_tool_calling_feeds_results_back_to_the_llm():
    client = _FakeStreamingClient(
        rounds=[
            [
                openai_tool_chunk(0, call_id="call_1", name="echo", arguments='{"message": "oi"}'),
                {"choices": [{"delta": {}, "finish_reason": "tool_calls"}]},
            ],
            [openai_text_chunk("pronto")],
        ]
    )

    list(stream_tool_calling(client, [Message(role="user", content="diga oi")], make_registry()))

    second_round = client.conversations[1]
    assert [message.role for message in second_round] == ["user", "assistant", "tool"]
    assert second_round[-1].tool_results[0].content == {"message": "oi"}


def test_stream_tool_calling_reports_tool_failure_as_event():
    client = _FakeStreamingClient(
        rounds=[
            [
                openai_tool_chunk(0, call_id="call_1", name="missing", arguments="{}"),
                {"choices": [{"delta": {}, "finish_reason": "tool_calls"}]},
            ],
            [openai_text_chunk("desculpe")],
        ]
    )

    events = list(
        stream_tool_calling(client, [Message(role="user", content="oi")], make_registry())
    )
    tool_result = next(event for event in events if event.type == EVENT_TOOL_RESULT)

    assert tool_result.data["is_error"] is True
    assert "missing" in tool_result.data["content"]


def test_stream_tool_calling_enforces_max_rounds():
    tool_round = [
        openai_tool_chunk(0, call_id="call_1", name="echo", arguments='{"message": "loop"}'),
        {"choices": [{"delta": {}, "finish_reason": "tool_calls"}]},
    ]
    client = _FakeStreamingClient(rounds=[tool_round, tool_round])

    with pytest.raises(MaxToolRoundsExceededError):
        list(
            stream_tool_calling(
                client,
                [Message(role="user", content="oi")],
                make_registry(),
                max_rounds=2,
            )
        )


def test_http_client_stream_parses_sse_and_flags_stream_in_body():
    captured = {}
    body = (
        "".join(
            f"data: {json.dumps(chunk)}\n\n"
            for chunk in [openai_text_chunk("oi"), openai_text_chunk("!")]
        )
        + "data: [DONE]\n\n"
    )

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content)
        return httpx.Response(200, content=body.encode())

    client = HttpLLMClient(
        settings=Settings(_env_file=None, llm_api_key="sk-test", llm_model="gpt-4o-mini"),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    chunks = list(client.stream([Message(role="user", content="oi")]))

    assert captured["body"]["stream"] is True
    assert [chunk["choices"][0]["delta"]["content"] for chunk in chunks] == ["oi", "!"]


def test_http_client_stream_surfaces_error_body():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": {"message": "invalid key"}})

    client = HttpLLMClient(
        settings=Settings(_env_file=None, llm_api_key="sk-bad", llm_model="gpt-4o-mini"),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(httpx.HTTPStatusError):
        list(client.stream([Message(role="user", content="oi")]))
