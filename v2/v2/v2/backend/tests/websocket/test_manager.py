from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from app.main import app
from app.websocket.manager import WebSocketManager, ConnectionInfo, EventType, WebSocketMessage


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def mock_websocket() -> MagicMock:
    ws = MagicMock()
    ws.accept = AsyncMock()
    ws.send_json = AsyncMock()
    ws.close = AsyncMock()
    ws.receive_text = AsyncMock()
    ws.client_state = MagicMock()
    return ws


class TestWebSocketManager:
    def test_singleton(self) -> None:
        manager1 = WebSocketManager()
        manager2 = WebSocketManager()
        assert manager1 is manager2

    def test_connect_disconnect(self, mock_websocket: MagicMock) -> None:
        import asyncio
        manager = WebSocketManager()
        conn_id = asyncio.get_event_loop().run_until_complete(manager.connect(mock_websocket))
        assert conn_id in manager.connections
        asyncio.get_event_loop().run_until_complete(manager.disconnect(conn_id))
        assert conn_id not in manager.connections

    def test_subscribe_room(self, mock_websocket: MagicMock) -> None:
        import asyncio
        manager = WebSocketManager()
        conn_id = asyncio.get_event_loop().run_until_complete(manager.connect(mock_websocket))
        asyncio.get_event_loop().run_until_complete(manager.subscribe_room(conn_id, "room-1"))
        assert "room-1" in manager.room_subscriptions
        assert conn_id in manager.room_subscriptions["room-1"]
        asyncio.get_event_loop().run_until_complete(manager.disconnect(conn_id))

    def test_rate_limiter(self) -> None:
        import asyncio
        manager = WebSocketManager()
        conn_id = "test-conn"
        for _ in range(120):
            assert not manager.is_rate_limited(conn_id)
        assert manager.is_rate_limited(conn_id)

    def test_broadcast_to_room(self, mock_websocket: MagicMock) -> None:
        import asyncio
        manager = WebSocketManager()
        conn_id = asyncio.get_event_loop().run_until_complete(manager.connect(mock_websocket))
        asyncio.get_event_loop().run_until_complete(manager.subscribe_room(conn_id, "room-1"))
        message = WebSocketMessage(event=EventType.ANNOUNCEMENT, data={"text": "hello"}, room_id="room-1")
        asyncio.get_event_loop().run_until_complete(manager.broadcast_to_room("room-1", message))
        mock_websocket.send_json.assert_called()
        asyncio.get_event_loop().run_until_complete(manager.disconnect(conn_id))

    def test_get_stats(self, mock_websocket: MagicMock) -> None:
        import asyncio
        manager = WebSocketManager()
        asyncio.get_event_loop().run_until_complete(manager.connect(mock_websocket))
        stats = manager.get_stats()
        assert "total_connections" in stats
        assert stats["total_connections"] == 1
