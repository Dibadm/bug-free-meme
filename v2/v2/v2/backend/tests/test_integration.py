from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestHealthEndpoints:
    def test_health(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_health_live(self, client: TestClient) -> None:
        response = client.get("/health/live")
        assert response.status_code == 200
        assert response.json() == {"status": "alive"}

    def test_health_ready(self, client: TestClient) -> None:
        response = client.get("/health/ready")
        assert response.status_code in (200, 503)


class TestWebSocketRoot:
    def test_websocket_root(self, client: TestClient) -> None:
        with client.websocket_connect("/ws") as websocket:
            data = websocket.receive_json()
            assert data["event"] == "welcome"
