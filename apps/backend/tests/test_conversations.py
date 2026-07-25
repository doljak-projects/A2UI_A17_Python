from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401  (registra os models em Base.metadata)
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    """Cliente HTTP ligado a um SQLite descartável.

    Cada teste recebe um arquivo novo em `tmp_path`, então listagem e paginação
    são determinísticas e nada vaza entre testes. As tabelas são criadas com
    `create_all` (mais rápido); o `alembic upgrade head` é validado à parte.
    """
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db() -> Iterator[Session]:
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)
    engine.dispose()


def create_conversation(client: TestClient, title: str) -> dict:
    response = client.post("/api/conversations", json={"title": title})
    assert response.status_code == 201
    return response.json()


def test_create_returns_201_with_created_resource(client: TestClient):
    response = client.post("/api/conversations", json={"title": "Primeira conversa"})

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["title"] == "Primeira conversa"
    assert body["created_at"]
    assert body["updated_at"]


def test_create_strips_surrounding_whitespace(client: TestClient):
    assert create_conversation(client, "  Com espaços  ")["title"] == "Com espaços"


@pytest.mark.parametrize("title", ["", "   ", "x" * 201])
def test_create_rejects_invalid_title(client: TestClient, title: str):
    response = client.post("/api/conversations", json={"title": title})
    assert response.status_code == 422


def test_create_requires_title(client: TestClient):
    assert client.post("/api/conversations", json={}).status_code == 422


def test_list_returns_conversations_ordered_by_id(client: TestClient):
    for title in ("Primeira", "Segunda", "Terceira"):
        create_conversation(client, title)

    response = client.get("/api/conversations")

    assert response.status_code == 200
    assert [item["title"] for item in response.json()] == ["Primeira", "Segunda", "Terceira"]


def test_list_is_empty_without_conversations(client: TestClient):
    response = client.get("/api/conversations")

    assert response.status_code == 200
    assert response.json() == []


def test_list_applies_skip_and_limit(client: TestClient):
    for index in range(5):
        create_conversation(client, f"Conversa {index}")

    response = client.get("/api/conversations", params={"skip": 1, "limit": 2})

    assert response.status_code == 200
    assert [item["title"] for item in response.json()] == ["Conversa 1", "Conversa 2"]


@pytest.mark.parametrize("params", [{"skip": -1}, {"limit": 0}, {"limit": 101}])
def test_list_rejects_invalid_pagination(client: TestClient, params: dict):
    assert client.get("/api/conversations", params=params).status_code == 422


def test_get_returns_conversation_by_id(client: TestClient):
    created = create_conversation(client, "Conversa buscada")

    response = client.get(f"/api/conversations/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_returns_404_for_unknown_id(client: TestClient):
    response = client.get("/api/conversations/999")

    assert response.status_code == 404
    assert "999" in response.json()["detail"]


def test_update_changes_title(client: TestClient):
    created = create_conversation(client, "Título antigo")

    response = client.patch(f"/api/conversations/{created['id']}", json={"title": "Título novo"})

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Título novo"
    assert body["id"] == created["id"]
    assert body["created_at"] == created["created_at"]


def test_update_without_fields_keeps_current_values(client: TestClient):
    created = create_conversation(client, "Sem alteração")

    response = client.patch(f"/api/conversations/{created['id']}", json={})

    assert response.status_code == 200
    assert response.json()["title"] == "Sem alteração"


def test_update_rejects_empty_title(client: TestClient):
    created = create_conversation(client, "Título válido")

    response = client.patch(f"/api/conversations/{created['id']}", json={"title": ""})

    assert response.status_code == 422


def test_update_returns_404_for_unknown_id(client: TestClient):
    response = client.patch("/api/conversations/999", json={"title": "Fantasma"})

    assert response.status_code == 404


def test_delete_returns_204_and_removes_conversation(client: TestClient):
    created = create_conversation(client, "Para apagar")

    response = client.delete(f"/api/conversations/{created['id']}")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/api/conversations/{created['id']}").status_code == 404


def test_delete_returns_404_for_unknown_id(client: TestClient):
    assert client.delete("/api/conversations/999").status_code == 404
