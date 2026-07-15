from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.websocket.auth import authenticate_connection, validate_reconnect
from app.websocket.rate_limiter import WebSocketRateLimiter


@pytest.fixture
def mock_connection() -> MagicMock:
    connection = MagicMock()
    connection.token = "valid-token"
    connection.websocket = MagicMock()
    connection.websocket.send_json = AsyncMock()
    connection.websocket.close = AsyncMock()
    connection.user_id = None
    return connection


@pytest.fixture
def mock_db() -> MagicMock:
    db = MagicMock()
    return db


class TestWebSocketAuth:
    async def test_authenticate_missing_token(self, mock_connection: MagicMock, mock_db: MagicMock) -> None:
        mock_connection.token = None
        result = await authenticate_connection(mock_connection, mock_db)
        assert result is False

    async def test_validate_reconnect_valid(self, mock_connection: MagicMock) -> None:
        mock_connection.user_id = "user-1"
        result = await validate_reconnect(mock_connection, "user-1")
        assert result is True

    async def test_validate_reconnect_invalid(self, mock_connection: MagicMock) -> None:
        result = await validate_reconnect(mock_connection, "user-2")
        assert result is False


class TestWebSocketRateLimiter:
    def test_singleton(self) -> None:
        limiter1 = WebSocketRateLimiter()
        limiter2 = WebSocketRateLimiter()
        assert limiter1 is limiter2

    def test_is_allowed(self) -> None:
        limiter = WebSocketRateLimiter()
        for _ in range(120):
            assert limiter.is_allowed("test-key") is True
        assert limiter.is_allowed("test-key") is False

    def test_reset(self) -> None:
        limiter = WebSocketRateLimiter()
        for _ in range(120):
            limiter.is_allowed("test-key")
        limiter.reset("test-key")
        assert limiter.is_allowed("test-key") is True

    def test_get_remaining(self) -> None:
        limiter = WebSocketRateLimiter()
        assert limiter.get_remaining("test-key") == 120
        limiter.is_allowed("test-key")
        assert limiter.get_remaining("test-key") == 119
