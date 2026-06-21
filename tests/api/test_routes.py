import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


def test_health_returns_200(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_ok_status(client: TestClient) -> None:
    data = client.get("/health").json()
    assert data["status"] == "ok"


# ---------------------------------------------------------------------------
# WebSocket /ws/game
# ---------------------------------------------------------------------------


def test_websocket_connects(client: TestClient) -> None:
    with client.websocket_connect("/ws/game") as ws:
        data = ws.receive_json()
        assert data["type"] == "connected"


def test_websocket_ping_pong(client: TestClient) -> None:
    with client.websocket_connect("/ws/game") as ws:
        ws.receive_json()  # consume "connected" message
        ws.send_json({"type": "ping"})
        data = ws.receive_json()
        assert data["type"] == "pong"


def test_websocket_unknown_message_returns_error(client: TestClient) -> None:
    with client.websocket_connect("/ws/game") as ws:
        ws.receive_json()  # consume "connected" message
        ws.send_json({"type": "unknown_command"})
        data = ws.receive_json()
        assert data["type"] == "error"
