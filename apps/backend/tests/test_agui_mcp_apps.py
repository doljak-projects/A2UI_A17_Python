from __future__ import annotations

import pytest
from ag_ui.core import RunAgentInput

from app.agui.a2ui_constants import MCP_APPS_ACTIVITY_TYPE, WEATHER_MCP_RESOURCE_URI
from app.agui.agent import WeatherMcpAppsActivityAgent
from app.agui.mcp_proxy import execute_proxied_mcp_request
from app.schemas.weather import WeatherResult

FAKE_RESULT = WeatherResult(
    city="Sao Paulo", temperature_c=18.1, description="Parcialmente nublado", humidity=77
)


def _input(forwarded_props: dict | None = None) -> RunAgentInput:
    return RunAgentInput(
        thread_id="t1",
        run_id="r1",
        state=None,
        messages=[],
        tools=[],
        context=[],
        forwarded_props=forwarded_props or {},
    )


@pytest.fixture
def mock_get_weather(monkeypatch):
    monkeypatch.setattr("app.agui.agent.get_weather", lambda city: FAKE_RESULT)


def test_weather_mcp_apps_agent_emits_mcp_apps_snapshot(mock_get_weather):
    events = list(WeatherMcpAppsActivityAgent().run(_input()))

    assert [event.type.value for event in events] == [
        "RUN_STARTED",
        "ACTIVITY_SNAPSHOT",
        "RUN_FINISHED",
    ]
    snapshot = next(event for event in events if event.type.value == "ACTIVITY_SNAPSHOT")
    assert snapshot.activity_type == MCP_APPS_ACTIVITY_TYPE
    assert snapshot.content["resourceUri"] == WEATHER_MCP_RESOURCE_URI
    assert snapshot.content["result"]["structuredContent"]["city"] == "Sao Paulo"


def test_mcp_proxy_reads_weather_resource():
    result = execute_proxied_mcp_request(
        {
            "method": "resources/read",
            "params": {"uri": WEATHER_MCP_RESOURCE_URI},
        }
    )

    assert result["contents"][0]["uri"] == WEATHER_MCP_RESOURCE_URI
    assert "Weather MCP App" in result["contents"][0]["text"]


def test_mcp_proxy_calls_a_registered_tool():
    # Usa a tool `echo` (sem dependência externa) em vez de `get_weather` — o
    # proxy é agnóstico à tool chamada, então não precisa da WeatherAPI real
    # configurada só pra validar o roteamento `tools/call`.
    result = execute_proxied_mcp_request(
        {
            "method": "tools/call",
            "params": {"name": "echo", "arguments": {"message": "oi"}},
        }
    )

    assert result["content"][0]["text"] or result["structuredContent"]


def test_agent_routes_proxied_mcp_request_instead_of_normal_flow(mock_get_weather):
    proxied_input = _input(
        forwarded_props={
            "__proxiedMCPRequest": {
                "method": "resources/read",
                "params": {"uri": WEATHER_MCP_RESOURCE_URI},
            }
        }
    )

    events = list(WeatherMcpAppsActivityAgent().run(proxied_input))

    assert [event.type.value for event in events] == ["RUN_STARTED", "RUN_FINISHED"]
    assert "ACTIVITY_SNAPSHOT" not in [event.type.value for event in events]
