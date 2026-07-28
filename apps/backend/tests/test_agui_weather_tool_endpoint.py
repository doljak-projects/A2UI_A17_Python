import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.schemas.weather import WeatherResult

FAKE_RESULT = WeatherResult(
    city="Sao Paulo", temperature_c=18.1, description="Parcialmente nublado", humidity=77
)


@pytest.fixture
def client():
    return TestClient(create_app())


def parse_sse_lines(body: str) -> list[str]:
    lines = []
    for frame in body.strip().split("\n\n"):
        for line in frame.splitlines():
            if line.startswith("data:"):
                lines.append(line)
    return lines


def test_weather_tool_demo_streams_sse(client, monkeypatch):
    monkeypatch.setattr("app.agui.agent.get_weather", lambda city: FAKE_RESULT)

    response = client.get("/api/agui/weather-tool-demo")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")


def test_weather_tool_demo_emits_full_event_sequence_with_real_payload(client, monkeypatch):
    monkeypatch.setattr("app.agui.agent.get_weather", lambda city: FAKE_RESULT)

    response = client.get("/api/agui/weather-tool-demo")

    frames = parse_sse_lines(response.text)

    assert len(frames) == 6
    assert '"type":"RUN_STARTED"' in frames[0]
    assert '"type":"TOOL_CALL_START"' in frames[1]
    assert '"type":"TOOL_CALL_ARGS"' in frames[2]
    assert '"type":"TOOL_CALL_END"' in frames[3]
    assert '"type":"TOOL_CALL_RESULT"' in frames[4]
    assert "Parcialmente nublado" in frames[4]
    assert '"type":"RUN_FINISHED"' in frames[5]


def test_weather_tool_demo_reports_get_weather_failure_as_run_error(client, monkeypatch):
    def explode(city):
        raise RuntimeError("chave da WeatherAPI inválida")

    monkeypatch.setattr("app.agui.agent.get_weather", explode)

    response = client.get("/api/agui/weather-tool-demo")

    frames = parse_sse_lines(response.text)

    assert '"type":"RUN_ERROR"' in frames[-1]
    assert "chave da WeatherAPI inválida" in frames[-1]
    assert not any('"type":"TOOL_CALL_RESULT"' in frame for frame in frames)
