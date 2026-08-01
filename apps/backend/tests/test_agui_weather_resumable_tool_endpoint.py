import json

import pytest
from fastapi.testclient import TestClient

from app.agui.agent import WeatherResumableToolCallAgent
from app.main import create_app

WEATHER_JSON = json.dumps(
    {"city": "São Paulo", "temperature_c": 24.7, "description": "Ensolarado", "humidity": 35},
    ensure_ascii=False,
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


def _base_body(**overrides):
    body = {
        "threadId": "t1",
        "runId": "r1",
        "state": None,
        "messages": [],
        "tools": [],
        "context": [],
        "forwardedProps": {},
    }
    body.update(overrides)
    return body


def test_accepts_a_real_post_body_and_streams_sse(client):
    response = client.post("/api/agui/weather-tool-agent-demo", json=_base_body())

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")


def test_without_tool_result_emits_pending_tool_call(client):
    response = client.post("/api/agui/weather-tool-agent-demo", json=_base_body())

    frames = parse_sse_lines(response.text)

    assert len(frames) == 5
    assert '"type":"TOOL_CALL_START"' in frames[1]
    assert not any('"type":"TEXT_MESSAGE_START"' in frame for frame in frames)


def test_with_tool_result_emits_text_reply(client):
    body = _base_body(
        messages=[
            {
                "id": "m1",
                "role": "tool",
                "content": WEATHER_JSON,
                "toolCallId": WeatherResumableToolCallAgent.TOOL_CALL_ID,
            }
        ],
    )

    response = client.post("/api/agui/weather-tool-agent-demo", json=body)

    frames = parse_sse_lines(response.text)

    assert '"type":"TEXT_MESSAGE_CONTENT"' in frames[2]
    assert "São Paulo" in frames[2]
    assert not any('"type":"TOOL_CALL_START"' in frame for frame in frames)


def test_rejects_a_malformed_body(client):
    response = client.post("/api/agui/weather-tool-agent-demo", json={"threadId": "t1"})

    assert response.status_code == 422
