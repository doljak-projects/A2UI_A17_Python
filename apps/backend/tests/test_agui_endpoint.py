import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    return TestClient(create_app())


def parse_sse_types(body: str) -> list[str]:
    types = []
    for frame in body.strip().split("\n\n"):
        for line in frame.splitlines():
            if line.startswith("data:"):
                types.append(line)
    return types


def test_agui_demo_streams_sse(client):
    response = client.get("/api/agui/demo")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert response.headers["x-accel-buffering"] == "no"


def test_agui_demo_emits_full_event_sequence(client):
    response = client.get("/api/agui/demo")

    frames = parse_sse_types(response.text)

    assert len(frames) == 5
    assert '"type":"RUN_STARTED"' in frames[0]
    assert '"type":"TEXT_MESSAGE_START"' in frames[1]
    assert '"type":"TEXT_MESSAGE_CONTENT"' in frames[2]
    assert '"type":"TEXT_MESSAGE_END"' in frames[3]
    assert '"type":"RUN_FINISHED"' in frames[4]
