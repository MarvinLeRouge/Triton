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
# WebSocket /ws/game — simulation state streaming
# ---------------------------------------------------------------------------


def test_websocket_sends_initial_state(client: TestClient) -> None:
    with client.websocket_connect("/ws/game") as ws:
        data = ws.receive_json()
        assert data["turn"] == 0
        assert data["result"] == "in_progress"


def test_initial_state_has_required_keys(client: TestClient) -> None:
    with client.websocket_connect("/ws/game") as ws:
        data = ws.receive_json()
        assert {"turn", "result", "mothership", "drones", "vessel"} <= set(data.keys())


def test_mothership_position_in_initial_state(client: TestClient) -> None:
    with client.websocket_connect("/ws/game") as ws:
        data = ws.receive_json()
        ms = data["mothership"]
        assert "row" in ms and "col" in ms
        assert isinstance(ms["row"], int) and isinstance(ms["col"], int)


def test_drones_list_in_initial_state(client: TestClient) -> None:
    with client.websocket_connect("/ws/game") as ws:
        data = ws.receive_json()
        drones = data["drones"]
        assert isinstance(drones, list)
        assert len(drones) > 0
        assert all("row" in d and "col" in d for d in drones)


def test_second_frame_advances_turn(client: TestClient) -> None:
    with client.websocket_connect("/ws/game") as ws:
        first = ws.receive_json()
        second = ws.receive_json()
        assert second["turn"] == first["turn"] + 1


def test_result_is_valid_string(client: TestClient) -> None:
    valid = {"in_progress", "blue_wins", "red_wins"}
    with client.websocket_connect("/ws/game") as ws:
        data = ws.receive_json()
        assert data["result"] in valid


def test_initial_state_has_detection_events_key(client: TestClient) -> None:
    with client.websocket_connect("/ws/game") as ws:
        data = ws.receive_json()
        assert "detection_events" in data
        assert isinstance(data["detection_events"], list)


def test_drones_have_heading_field(client: TestClient) -> None:
    with client.websocket_connect("/ws/game") as ws:
        data = ws.receive_json()
        assert all("heading" in d for d in data["drones"])
        assert all(len(d["heading"]) == 2 for d in data["drones"])
