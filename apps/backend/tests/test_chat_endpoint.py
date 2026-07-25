import json

import pytest
from fastapi.testclient import TestClient

from app.llm.streaming import StreamEvent
from app.main import create_app


@pytest.fixture
def client():
    return TestClient(create_app())


def parse_sse(body: str) -> list[tuple[str, dict]]:
    events = []
    for frame in body.strip().split("\n\n"):
        lines = dict(line.split(": ", 1) for line in frame.splitlines())
        events.append((lines["event"], json.loads(lines["data"])))
    return events


def fake_stream(events):
    def _stream(client, messages, registry=None, max_rounds=5):
        yield from events

    return _stream


def test_chat_streams_events_as_sse(client, monkeypatch):
    monkeypatch.setattr("app.api.routes.chat.HttpLLMClient", lambda: object())
    monkeypatch.setattr(
        "app.api.routes.chat.stream_tool_calling",
        fake_stream(
            [
                StreamEvent("tool_call", {"id": "c1", "name": "get_weather"}),
                StreamEvent("delta", {"text": "São Paulo"}),
                StreamEvent("done", {"text": "São Paulo", "rounds": 2}),
            ]
        ),
    )

    response = client.post("/api/chat", json={"messages": [{"role": "user", "content": "clima?"}]})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert response.headers["x-accel-buffering"] == "no"
    assert parse_sse(response.text) == [
        ("tool_call", {"id": "c1", "name": "get_weather"}),
        ("delta", {"text": "São Paulo"}),
        ("done", {"text": "São Paulo", "rounds": 2}),
    ]


def test_chat_reports_failure_as_error_event(client, monkeypatch):
    def explode():
        raise RuntimeError("provedor fora do ar")

    monkeypatch.setattr("app.api.routes.chat.HttpLLMClient", explode)

    response = client.post("/api/chat", json={"messages": [{"role": "user", "content": "oi"}]})

    assert response.status_code == 200
    assert parse_sse(response.text) == [("error", {"message": "provedor fora do ar"})]


def test_chat_rejects_empty_message_list(client):
    response = client.post("/api/chat", json={"messages": []})

    assert response.status_code == 422


def test_chat_rejects_unknown_role(client):
    response = client.post("/api/chat", json={"messages": [{"role": "tool", "content": "oi"}]})

    assert response.status_code == 422
