from __future__ import annotations

import json

from ag_ui.core import RunAgentInput

from app.agui.agent import WeatherClientToolCallAgent


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


def test_full_event_sequence_leaves_the_tool_call_unresolved():
    events = list(WeatherClientToolCallAgent().run(_input()))

    sequence = [e.type.value for e in events]

    assert sequence == [
        "RUN_STARTED",
        "TOOL_CALL_START",
        "TOOL_CALL_ARGS",
        "TOOL_CALL_END",
        "RUN_FINISHED",
    ]
    assert "TOOL_CALL_RESULT" not in sequence


def test_tool_call_start_names_show_weather():
    events = list(WeatherClientToolCallAgent().run(_input()))

    start = next(e for e in events if e.type.value == "TOOL_CALL_START")

    assert start.tool_call_name == "show_weather"


def test_tool_call_args_carries_the_city_as_json():
    events = list(WeatherClientToolCallAgent().run(_input()))

    args = next(e for e in events if e.type.value == "TOOL_CALL_ARGS")

    assert json.loads(args.delta) == {"city": WeatherClientToolCallAgent.CITY}


def test_tool_call_events_share_the_same_tool_call_id():
    events = list(WeatherClientToolCallAgent().run(_input()))

    tool_events = [e for e in events if e.type.value.startswith("TOOL_CALL_")]
    tool_call_ids = {e.tool_call_id for e in tool_events}

    assert tool_call_ids == {WeatherClientToolCallAgent.TOOL_CALL_ID}


def test_run_started_and_finished_carry_matching_ids():
    events = list(WeatherClientToolCallAgent().run(_input(thread_id="t9", run_id="r9")))

    started, finished = events[0], events[-1]

    assert (started.thread_id, started.run_id) == ("t9", "r9")
    assert (finished.thread_id, finished.run_id) == ("t9", "r9")
