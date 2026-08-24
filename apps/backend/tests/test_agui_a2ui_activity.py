from __future__ import annotations

import pytest
from ag_ui.core import RunAgentInput, UserMessage

from app.agui.a2ui_constants import A2UI_SURFACE_ACTIVITY_TYPE
from app.agui.a2ui_weather_card import create_humidity_card, create_weather_card
from app.agui.agent import WeatherA2UiActivityAgent
from app.agui.weather_intent import CORDIAL_REPLY
from app.schemas.weather import WeatherResult


class _FakeStreamingLLM:
    provider = "openai"

    def __init__(self, chunks: list[dict] | None = None) -> None:
        self.chunks = chunks or [
            {"choices": [{"delta": {"content": "Oi! "}}]},
            {"choices": [{"delta": {"content": "Como posso ajudar?"}}]},
            {"choices": [{"delta": {}, "finish_reason": "stop"}]},
        ]
        self.conversations: list[list] = []

    def stream(self, messages, tools=None):
        self.conversations.append(list(messages))
        yield from self.chunks

FAKE_RESULT = WeatherResult(
    city="Sao Paulo", temperature_c=18.1, description="Parcialmente nublado", humidity=77
)


def _input(
    thread_id: str = "t1",
    run_id: str = "r1",
    content: str | None = None,
) -> RunAgentInput:
    messages = []
    if content is not None:
        messages = [UserMessage(id="u1", content=content)]
    return RunAgentInput(
        thread_id=thread_id,
        run_id=run_id,
        state=None,
        messages=messages,
        tools=[],
        context=[],
        forwarded_props={},
    )


@pytest.fixture
def mock_get_weather(monkeypatch):
    def _fake(city: str) -> WeatherResult:
        return WeatherResult(
            city=city,
            temperature_c=18.1,
            description="Ensolarado",
            humidity=42,
        )

    monkeypatch.setattr("app.agui.agent.get_weather", _fake)


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


def test_create_weather_card_is_temperature_only():
    components = create_weather_card("surface-1", "catalog-1", FAKE_RESULT)[1]["updateComponents"][
        "components"
    ]
    by_id = {component["id"]: component for component in components}

    assert by_id["root"]["component"] == "TemperatureHero"
    assert "card-humidity" not in by_id


def test_create_humidity_card_is_humidity_only():
    components = create_humidity_card("surface-1", "catalog-1", FAKE_RESULT)[1]["updateComponents"][
        "components"
    ]
    by_id = {component["id"]: component for component in components}

    assert by_id["root"]["component"] == "HumidityGauge"
    assert by_id["root"]["humidity"] == {"path": "/humidity"}


def test_weather_a2ui_agent_emits_cordial_text_then_weather_card(mock_get_weather):
    events = list(
        WeatherA2UiActivityAgent().run(
            _input(run_id="run-42", content="clima em rio de janeiro")
        )
    )

    assert [event.type.value for event in events] == [
        "RUN_STARTED",
        "TEXT_MESSAGE_START",
        "TEXT_MESSAGE_CONTENT",
        "TEXT_MESSAGE_END",
        "ACTIVITY_SNAPSHOT",
        "RUN_FINISHED",
    ]
    text = next(event for event in events if event.type.value == "TEXT_MESSAGE_CONTENT")
    assert text.delta == CORDIAL_REPLY

    snapshot = next(event for event in events if event.type.value == "ACTIVITY_SNAPSHOT")
    assert snapshot.activity_type == A2UI_SURFACE_ACTIVITY_TYPE
    assert snapshot.content["cardKind"] == "weather"
    assert snapshot.content["operations"][0]["createSurface"]["surfaceId"] == (
        "weather-chat-surface-weather-run-42"
    )
    assert snapshot.content["operations"][2]["updateDataModel"]["value"]["city"] == (
        "Rio de Janeiro"
    )


def test_weather_a2ui_agent_picks_humidity_card(mock_get_weather):
    events = list(
        WeatherA2UiActivityAgent().run(_input(run_id="run-h", content="umidade em curitiba"))
    )
    snapshot = next(event for event in events if event.type.value == "ACTIVITY_SNAPSHOT")

    assert snapshot.content["cardKind"] == "humidity"
    components = snapshot.content["operations"][1]["updateComponents"]["components"]
    by_id = {component["id"]: component for component in components}
    assert by_id["root"]["component"] == "HumidityGauge"
    assert snapshot.content["operations"][2]["updateDataModel"]["value"]["city"] == "Curitiba"


def test_weather_a2ui_agent_uses_unique_surface_per_run(mock_get_weather):
    first = list(
        WeatherA2UiActivityAgent().run(_input(run_id="run-a", content="clima em lisboa"))
    )
    second = list(
        WeatherA2UiActivityAgent().run(_input(run_id="run-b", content="clima em lisboa"))
    )

    first_surface = next(
        event for event in first if event.type.value == "ACTIVITY_SNAPSHOT"
    ).content["operations"][0]["createSurface"]["surfaceId"]
    second_surface = next(
        event for event in second if event.type.value == "ACTIVITY_SNAPSHOT"
    ).content["operations"][0]["createSurface"]["surfaceId"]

    assert first_surface != second_surface
    assert first_surface.startswith("weather-chat-surface-")
    assert second_surface.startswith("weather-chat-surface-")


def test_weather_a2ui_agent_uses_llm_without_weather_intent(mock_get_weather, monkeypatch):
    called: list[str] = []

    def _guard(city: str):
        called.append(city)
        raise AssertionError("get_weather não deveria ser chamado sem intenção")

    monkeypatch.setattr("app.agui.agent.get_weather", _guard)
    llm = _FakeStreamingLLM()
    events = list(
        WeatherA2UiActivityAgent(llm_client=llm).run(_input(content="oi, tudo bem?"))
    )

    assert called == []
    assert [event.type.value for event in events] == [
        "RUN_STARTED",
        "TEXT_MESSAGE_START",
        "TEXT_MESSAGE_CONTENT",
        "TEXT_MESSAGE_CONTENT",
        "TEXT_MESSAGE_END",
        "RUN_FINISHED",
    ]
    assert not any(event.type.value == "ACTIVITY_SNAPSHOT" for event in events)
    text = "".join(
        event.delta for event in events if event.type.value == "TEXT_MESSAGE_CONTENT"
    )
    assert text == "Oi! Como posso ajudar?"
