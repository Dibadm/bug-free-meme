from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.core.logging import get_logger
from app.models.models import UserStatus
from app.services.auth_service import AuthService
from app.websocket.events import EventType, WebSocketMessage
from app.websocket.manager import ConnectionInfo, WebSocketManager

logger = get_logger(__name__)


async def authenticate_connection(connection: ConnectionInfo, db_session: Any) -> bool:
    if not connection.token:
        await connection.websocket.send_json(
            WebSocketMessage(event=EventType.ERROR, data={"error": "Authentication required"}).to_dict()
        )
        await connection.websocket.close(code=4001)
        return False
    try:
        auth_service = AuthService(db_session)
        session = await auth_service.get_session_by_token(connection.token)
        if not session or session.revoked_at or session.expires_at < datetime.now(timezone.utc):
            await connection.websocket.send_json(
                WebSocketMessage(event=EventType.ERROR, data={"error": "Invalid or expired session"}).to_dict()
            )
            await connection.websocket.close(code=4002)
            return False
        user = await auth_service.user_repo.get_by_id(session.user_id)
        if not user or user.status in (UserStatus.BANNED, UserStatus.DELETED):
            await connection.websocket.send_json(
                WebSocketMessage(event=EventType.ERROR, data={"error": "User not allowed"}).to_dict()
            )
            await connection.websocket.close(code=4003)
            return False
        connection.user_id = user.id
        connection.device_info = session.device_info or connection.device_info
        return True
    except Exception as exc:
        logger.error("ws_auth_error", error=str(exc))
        await connection.websocket.close(code=4000)
        return False


async def validate_reconnect(connection: ConnectionInfo, expected_user_id: UUID) -> bool:
    if connection.user_id != expected_user_id:
        return False
    if not connection.token:
        return False
    return True
