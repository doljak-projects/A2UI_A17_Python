from __future__ import annotations

import json

from ag_ui.core import RunAgentInput, ToolMessage

from app.agui.agent import WeatherResumableToolCallAgent

WEATHER_JSON = json.dumps(
    {"city": "São Paulo", "temperature_c": 24.7, "description": "Ensolarado", "humidity": 35},
    ensure_ascii=False,
)


def _input(messages: list | None = None, thread_id: str = "t1", run_id: str = "r1") -> RunAgentInput:
    return RunAgentInput(
        thread_id=thread_id,
        run_id=run_id,
        state=None,
        messages=messages or [],
        tools=[],
        context=[],
        forwarded_props={},
    )


def _tool_result_message(content: str = WEATHER_JSON, tool_call_id: str | None = None) -> ToolMessage:
    return ToolMessage(
        id="m1",
        role="tool",
        content=content,
        toolCallId=tool_call_id or WeatherResumableToolCallAgent.TOOL_CALL_ID,
    )


class TestWithoutToolResult:
    def test_emits_pending_tool_call_sequence(self):
        events = list(WeatherResumableToolCallAgent().run(_input()))

        sequence = [e.type.value for e in events]

        assert sequence == [
            "RUN_STARTED",
            "TOOL_CALL_START",
            "TOOL_CALL_ARGS",
            "TOOL_CALL_END",
            "RUN_FINISHED",
        ]

    def test_tool_call_start_names_show_weather(self):
        events = list(WeatherResumableToolCallAgent().run(_input()))

        start = next(e for e in events if e.type.value == "TOOL_CALL_START")

        assert start.tool_call_name == "show_weather"

    def test_ignores_tool_message_with_a_different_tool_call_id(self):
        messages = [_tool_result_message(tool_call_id="other-id")]

        events = list(WeatherResumableToolCallAgent().run(_input(messages=messages)))

        sequence = [e.type.value for e in events]
        assert "TOOL_CALL_START" in sequence
        assert "TEXT_MESSAGE_START" not in sequence


class TestWithToolResult:
    def test_emits_text_reply_instead_of_a_new_tool_call(self):
        messages = [_tool_result_message()]

        events = list(WeatherResumableToolCallAgent().run(_input(messages=messages)))

        sequence = [e.type.value for e in events]

        assert sequence == [
            "RUN_STARTED",
            "TEXT_MESSAGE_START",
            "TEXT_MESSAGE_CONTENT",
            "TEXT_MESSAGE_END",
            "RUN_FINISHED",
        ]

    def test_reply_mentions_the_received_weather_data(self):
        messages = [_tool_result_message()]

        events = list(WeatherResumableToolCallAgent().run(_input(messages=messages)))

        content = next(e for e in events if e.type.value == "TEXT_MESSAGE_CONTENT")

        assert "São Paulo" in content.delta
        assert "24.7" in content.delta
        assert "Ensolarado" in content.delta
        assert "35" in content.delta


def test_run_started_and_finished_carry_matching_ids():
    events = list(WeatherResumableToolCallAgent().run(_input(thread_id="t9", run_id="r9")))

    started, finished = events[0], events[-1]

    assert (started.thread_id, started.run_id) == ("t9", "r9")
    assert (finished.thread_id, finished.run_id) == ("t9", "r9")
