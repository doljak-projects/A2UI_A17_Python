from __future__ import annotations

import pytest
from ag_ui.core import RunAgentInput

from app.agui.agent import WeatherDashboardActivityAgent
from app.agui.dashboard_cache import dashboard_structure_cache
from app.agui.dashboard_dsl import dsl_from_cities, hash_dsl
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


@pytest.fixture(autouse=True)
def _clear_dashboard_cache():
    dashboard_structure_cache.clear()
    yield
    dashboard_structure_cache.clear()


@pytest.fixture
def mock_get_weather(monkeypatch):
    monkeypatch.setattr("app.agui.agent.get_weather", lambda city: FAKE_RESULT)


def test_dashboard_dsl_hash_is_stable():
    dsl = dsl_from_cities(["São Paulo", "Rio de Janeiro"])
    assert hash_dsl(dsl) == hash_dsl(dsl)


def test_weather_dashboard_agent_uses_cache_on_second_run(mock_get_weather):
    agent = WeatherDashboardActivityAgent()
    first = list(agent.run(_input(run_id="r1")))
    second = list(agent.run(_input(run_id="r2")))

    first_snapshot = next(event for event in first if event.type.value == "ACTIVITY_SNAPSHOT")
    second_snapshot = next(event for event in second if event.type.value == "ACTIVITY_SNAPSHOT")

    assert first_snapshot.content["cacheHit"] is False
    assert second_snapshot.content["cacheHit"] is True
    assert (
        first_snapshot.content["operations"][1]["updateComponents"]["components"]
        == second_snapshot.content["operations"][1]["updateComponents"]["components"]
    )
