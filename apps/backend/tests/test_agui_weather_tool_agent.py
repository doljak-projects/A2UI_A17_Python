from __future__ import annotations

import json

import pytest
from ag_ui.core import RunAgentInput

from app.agui.agent import WeatherToolCallAgent
from app.schemas.weather import WeatherResult

FAKE_RESULT = WeatherResult(
    city="Sao Paulo", temperature_c=18.1, description="Parcialmente nublado", humidity=77
)


def _input(thread_id: str = "t1", run_id: str = "r1") -> RunAgentInput:
    return RunAgentInput(
        thread_id=thread_id,
        run_id=run_id,
        state=None,
        messages=[],
        tools=[],
        context=[],
        forwarded_props={},
    )


@pytest.fixture
def mock_get_weather(monkeypatch):
    monkeypatch.setattr("app.agui.agent.get_weather", lambda city: FAKE_RESULT)


def test_full_event_sequence_matches_the_tutorial(mock_get_weather):
    events = list(WeatherToolCallAgent().run(_input()))

    sequence = [e.type.value for e in events]

    assert sequence == [
        "RUN_STARTED",
        "TOOL_CALL_START",
        "TOOL_CALL_ARGS",
        "TOOL_CALL_END",
        "TOOL_CALL_RESULT",
        "RUN_FINISHED",
    ]


def test_tool_call_events_share_the_same_tool_call_id(mock_get_weather):
    events = list(WeatherToolCallAgent().run(_input()))

    tool_events = [e for e in events if e.type.value.startswith("TOOL_CALL_")]
    tool_call_ids = {e.tool_call_id for e in tool_events}

    assert tool_call_ids == {WeatherToolCallAgent.TOOL_CALL_ID}


def test_tool_call_start_names_get_weather(mock_get_weather):
    events = list(WeatherToolCallAgent().run(_input()))

    start = next(e for e in events if e.type.value == "TOOL_CALL_START")

    assert start.tool_call_name == "get_weather"


def test_tool_call_args_carries_the_city_as_json(mock_get_weather):
    events = list(WeatherToolCallAgent().run(_input()))

    args = next(e for e in events if e.type.value == "TOOL_CALL_ARGS")

    assert json.loads(args.delta) == {"city": WeatherToolCallAgent.CITY}


def test_tool_call_result_carries_the_real_get_weather_payload(mock_get_weather):
    events = list(WeatherToolCallAgent().run(_input()))

    result = next(e for e in events if e.type.value == "TOOL_CALL_RESULT")

    assert json.loads(result.content) == json.loads(FAKE_RESULT.model_dump_json())
    assert result.role == "tool"


def test_run_started_and_finished_carry_matching_ids(mock_get_weather):
    events = list(WeatherToolCallAgent().run(_input(thread_id="t9", run_id="r9")))

    started, finished = events[0], events[-1]

    assert (started.thread_id, started.run_id) == ("t9", "r9")
    assert (finished.thread_id, finished.run_id) == ("t9", "r9")


def test_calls_get_weather_with_the_configured_city(monkeypatch):
    calls: list[str] = []
    monkeypatch.setattr("app.agui.agent.get_weather", lambda city: calls.append(city) or FAKE_RESULT)

    list(WeatherToolCallAgent().run(_input()))

    assert calls == [WeatherToolCallAgent.CITY]
