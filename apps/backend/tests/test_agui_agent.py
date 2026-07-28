from __future__ import annotations

from ag_ui.core import RunAgentInput

from app.agui.agent import WeatherChatAgent


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


def test_emits_run_started_first_with_matching_ids():
    events = list(WeatherChatAgent().run(_input(thread_id="t1", run_id="r1")))

    first = events[0]
    assert first.type.value == "RUN_STARTED"
    assert first.thread_id == "t1"
    assert first.run_id == "r1"


def test_emits_run_finished_last_with_matching_ids():
    events = list(WeatherChatAgent().run(_input(thread_id="t1", run_id="r1")))

    last = events[-1]
    assert last.type.value == "RUN_FINISHED"
    assert last.thread_id == "t1"
    assert last.run_id == "r1"


def test_text_message_events_share_the_same_message_id_and_wrap_content():
    events = list(WeatherChatAgent().run(_input()))

    text_events = [e for e in events if e.type.value.startswith("TEXT_MESSAGE_")]
    types = [e.type.value for e in text_events]

    assert types[0] == "TEXT_MESSAGE_START"
    assert types[-1] == "TEXT_MESSAGE_END"
    assert "TEXT_MESSAGE_CONTENT" in types

    message_ids = {e.message_id for e in text_events}
    assert message_ids == {WeatherChatAgent.MESSAGE_ID}


def test_content_deltas_are_non_empty_strings():
    events = list(WeatherChatAgent().run(_input()))

    content_events = [e for e in events if e.type.value == "TEXT_MESSAGE_CONTENT"]

    assert content_events
    assert all(isinstance(e.delta, str) and e.delta for e in content_events)


def test_full_event_sequence_matches_the_tutorial():
    events = list(WeatherChatAgent().run(_input()))

    sequence = [e.type.value for e in events]

    assert sequence == [
        "RUN_STARTED",
        "TEXT_MESSAGE_START",
        "TEXT_MESSAGE_CONTENT",
        "TEXT_MESSAGE_END",
        "RUN_FINISHED",
    ]
