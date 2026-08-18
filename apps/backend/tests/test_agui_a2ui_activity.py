from __future__ import annotations

import pytest

from app.agui.a2ui_constants import A2UI_SURFACE_ACTIVITY_TYPE
from app.agui.a2ui_weather_card import create_weather_card
from app.agui.agent import WeatherA2UiActivityAgent
from app.schemas.weather import WeatherResult
from ag_ui.core import RunAgentInput

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


def test_create_weather_card_emits_three_protocol_messages():
    messages = create_weather_card("surface-1", "catalog-1", FAKE_RESULT)

    assert [next(iter(message)) for message in messages] == [
        "version",
        "version",
        "version",
    ]
    assert messages[0]["createSurface"]["surfaceId"] == "surface-1"
    assert messages[1]["updateComponents"]["surfaceId"] == "surface-1"
    assert messages[2]["updateDataModel"]["value"]["city"] == "Sao Paulo"


def test_weather_a2ui_agent_emits_activity_snapshot(mock_get_weather):
    events = list(WeatherA2UiActivityAgent().run(_input()))

    assert [event.type.value for event in events] == [
        "RUN_STARTED",
        "ACTIVITY_SNAPSHOT",
        "RUN_FINISHED",
    ]
    snapshot = next(event for event in events if event.type.value == "ACTIVITY_SNAPSHOT")
    assert snapshot.activity_type == A2UI_SURFACE_ACTIVITY_TYPE
    assert "operations" in snapshot.content
    assert snapshot.content["operations"][0]["createSurface"]["surfaceId"] == "weather-chat-surface"
