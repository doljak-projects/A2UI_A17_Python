import pytest
from fastapi.testclient import TestClient

from app.main import create_app


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


def test_weather_tool_client_demo_streams_sse(client):
    response = client.get("/api/agui/weather-tool-client-demo")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")


def test_weather_tool_client_demo_emits_pending_tool_call_sequence(client):
    response = client.get("/api/agui/weather-tool-client-demo")

    frames = parse_sse_lines(response.text)

    assert len(frames) == 5
    assert '"type":"RUN_STARTED"' in frames[0]
    assert '"type":"TOOL_CALL_START"' in frames[1]
    assert '"show_weather"' in frames[1]
    assert '"type":"TOOL_CALL_ARGS"' in frames[2]
    assert '"type":"TOOL_CALL_END"' in frames[3]
    assert '"type":"RUN_FINISHED"' in frames[4]
    assert not any('"type":"TOOL_CALL_RESULT"' in frame for frame in frames)
