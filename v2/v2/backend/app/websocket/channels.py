from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.websocket.events import EventType, WebSocketMessage
from app.websocket.manager import WebSocketManager

ws_manager = WebSocketManager()


class RoomChannel:
    @staticmethod
    async def subscribe(conn_id: str, room_id: UUID) -> None:
        await ws_manager.subscribe_room(conn_id, room_id)

    @staticmethod
    async def unsubscribe(conn_id: str, room_id: UUID) -> None:
        await ws_manager.unsubscribe_room(conn_id, room_id)

    @staticmethod
    async def publish(room_id: UUID, event: EventType, data: dict[str, Any]) -> None:
        message = WebSocketMessage(event=event, data=data, room_id=room_id)
        await ws_manager.broadcast_to_room(room_id, message)

    @staticmethod
    async def publish_excluding(room_id: UUID, event: EventType, data: dict[str, Any], exclude_user: UUID) -> None:
        message = WebSocketMessage(event=event, data=data, room_id=room_id)
        await ws_manager.broadcast_to_room(room_id, message, exclude_user=exclude_user)


class UserChannel:
    @staticmethod
    async def send(user_id: UUID, event: EventType, data: dict[str, Any]) -> None:
        message = WebSocketMessage(event=event, data=data, user_id=user_id)
        await ws_manager.send_personal(user_id, message)

    @staticmethod
    async def broadcast(users: list[UUID], event: EventType, data: dict[str, Any]) -> None:
        for user_id in users:
            await UserChannel.send(user_id, event, data)


class AdminChannel:
    @staticmethod
    async def broadcast(event: EventType, data: dict[str, Any]) -> None:
        message = WebSocketMessage(event=event, data=data)
        await ws_manager.broadcast(message)

    @staticmethod
    async def system_alert(level: str, message: str) -> None:
        await AdminChannel.broadcast(
            EventType.ANNOUNCEMENT,
            {"level": level, "message": message, "timestamp": datetime.now(timezone.utc).isoformat()},
        )
