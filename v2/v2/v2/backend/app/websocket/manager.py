from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Coroutine

from fastapi import WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from starlette.websockets import WebSocketState

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EventType(str, Enum):
    ROOM_CREATED = "room.created"
    ROOM_UPDATED = "room.updated"
    ROOM_DELETED = "room.deleted"
    PLAYER_JOINED = "player.joined"
    PLAYER_LEFT = "player.left"
    CARD_PURCHASED = "card.purchased"
    CARD_AVAILABLE = "card.available"
    COUNTDOWN_STARTED = "countdown.started"
    COUNTDOWN_TICK = "countdown.tick"
    COUNTDOWN_ENDED = "countdown.ended"
    BALL_CALLED = "ball.called"
    BALLS_ANIMATED = "balls.animated"
    MARK_AUTO = "mark.auto"
    MARK_MANUAL = "mark.manual"
    WINNER_CLAIMED = "winner.claimed"
    WINNER_VALIDATED = "winner.validated"
    PRIZE_DISTRIBUTED = "prize.distributed"
    GAME_COMPLETED = "game.completed"
    GAME_PAUSED = "game.paused"
    GAME_RESUMED = "game.resumed"
    GAME_CANCELLED = "game.cancelled"
    LEADERBOARD_UPDATED = "leaderboard.updated"
    WALLET_UPDATED = "wallet.updated"
    ANNOUNCEMENT = "announcement"
    NOTIFICATION = "notification"
    CONNECTION_STATE = "connection.state"
    USER_PRESENCE = "user.presence"
    ERROR = "error"


class WebSocketMessage:
    def __init__(self, event: EventType, data: dict[str, Any], room_id: uuid.UUID | None = None, user_id: uuid.UUID | None = None):
        self.event = event
        self.data = data
        self.room_id = room_id
        self.user_id = user_id
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.id = str(uuid.uuid4())

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "event": self.event.value,
            "data": self.data,
            "room_id": str(self.room_id) if self.room_id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "timestamp": self.timestamp,
        }


class ConnectionInfo:
    def __init__(self, websocket: WebSocket, user_id: uuid.UUID | None = None, token: str | None = None, device_info: str = ""):
        self.websocket = websocket
        self.user_id = user_id
        self.token = token
        self.device_info = device_info
        self.connected_at = datetime.now(timezone.utc)
        self.last_heartbeat = datetime.now(timezone.utc)
        self.subscriptions: set[str] = set()
        self.is_alive = True

    def update_heartbeat(self) -> None:
        self.last_heartbeat = datetime.now(timezone.utc)


class WebSocketManager:
    _instance: WebSocketManager | None = None

    def __new__(cls) -> WebSocketManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self.connections: dict[str, ConnectionInfo] = {}
        self.user_connections: dict[str, set[str]] = defaultdict(set)
        self.room_subscriptions: dict[str, set[str]] = defaultdict(set)
        self.handlers: dict[EventType, list[Callable[[WebSocketMessage], Coroutine[Any, Any, None]]]] = defaultdict(list)
        self.rate_limiter: dict[str, list[float]] = defaultdict(list)
        self.rate_limit_window = 60
        self.rate_limit_max = 120
        self.heartbeat_interval = 30
        self.heartbeat_timeout = 90
        self.reconnect_window = 300
        self._heartbeat_task: asyncio.Task | None = None

    def register_handler(self, event: EventType, handler: Callable[[WebSocketMessage], Coroutine[Any, Any, None]]) -> None:
        self.handlers[event].append(handler)

    async def start(self) -> None:
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def stop(self) -> None:
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        for conn_id in list(self.connections.keys()):
            await self.disconnect(conn_id)

    async def connect(self, websocket: WebSocket, user_id: uuid.UUID | None = None, token: str | None = None, device_info: str = "") -> str:
        await websocket.accept()
        conn_id = str(uuid.uuid4())
        conn = ConnectionInfo(websocket=websocket, user_id=user_id, token=token, device_info=device_info)
        self.connections[conn_id] = conn
        if user_id:
            self.user_connections[str(user_id)].add(conn_id)
        logger.info("ws_connected", conn_id=conn_id, user_id=str(user_id) if user_id else None)
        return conn_id

    async def disconnect(self, conn_id: str) -> None:
        conn = self.connections.pop(conn_id, None)
        if not conn:
            return
        if conn.user_id:
            self.user_connections[str(conn.user_id)].discard(conn_id)
            if not self.user_connections[str(conn.user_id)]:
                del self.user_connections[str(conn.user_id)]
        for room in list(conn.subscriptions):
            self.room_subscriptions[room].discard(conn_id)
            if not self.room_subscriptions[room]:
                del self.room_subscriptions[room]
        if conn.websocket.client_state == WebSocketState.CONNECTED:
            await conn.websocket.close()
        logger.info("ws_disconnected", conn_id=conn_id, user_id=str(conn.user_id) if conn.user_id else None)

    async def disconnect_user(self, user_id: uuid.UUID) -> None:
        conn_ids = list(self.user_connections.get(str(user_id), set()))
        for conn_id in conn_ids:
            await self.disconnect(conn_id)

    def get_user_connections(self, user_id: uuid.UUID) -> list[ConnectionInfo]:
        return [self.connections[cid] for cid in self.user_connections.get(str(user_id), set()) if cid in self.connections]

    async def subscribe_room(self, conn_id: str, room_id: str | uuid.UUID) -> None:
        conn = self.connections.get(conn_id)
        if not conn:
            return
        room_str = str(room_id)
        conn.subscriptions.add(room_str)
        self.room_subscriptions[room_str].add(conn_id)

    async def unsubscribe_room(self, conn_id: str, room_id: str | uuid.UUID) -> None:
        conn = self.connections.get(conn_id)
        if not conn:
            return
        room_str = str(room_id)
        conn.subscriptions.discard(room_str)
        self.room_subscriptions[room_str].discard(conn_id)
        if not self.room_subscriptions[room_str]:
            del self.room_subscriptions[room_str]

    def is_rate_limited(self, conn_id: str) -> bool:
        now = time.time()
        self.rate_limiter[conn_id] = [t for t in self.rate_limiter.get(conn_id, []) if now - t < self.rate_limit_window]
        if len(self.rate_limiter[conn_id]) >= self.rate_limit_max:
            return True
        self.rate_limiter[conn_id].append(now)
        return False

    async def send_personal(self, user_id: uuid.UUID, message: WebSocketMessage) -> None:
        conns = self.get_user_connections(user_id)
        for conn in conns:
            try:
                await conn.websocket.send_json(message.to_dict())
            except Exception:
                await self.disconnect(str(id(conn)))

    async def broadcast_to_room(self, room_id: str | uuid.UUID, message: WebSocketMessage, exclude_user: uuid.UUID | None = None) -> None:
        room_str = str(room_id)
        conn_ids = list(self.room_subscriptions.get(room_str, set()))
        for conn_id in conn_ids:
            conn = self.connections.get(conn_id)
            if not conn or not conn.is_alive:
                continue
            if exclude_user and conn.user_id == exclude_user:
                continue
            try:
                await conn.websocket.send_json(message.to_dict())
            except Exception:
                await self.disconnect(conn_id)

    async def broadcast(self, message: WebSocketMessage) -> None:
        for conn in list(self.connections.values()):
            if not conn.is_alive:
                continue
            try:
                await conn.websocket.send_json(message.to_dict())
            except Exception:
                await self.disconnect(str(id(conn)))

    async def handle_message(self, conn_id: str, raw: str) -> None:
        conn = self.connections.get(conn_id)
        if not conn or not conn.is_alive:
            return
        if self.is_rate_limited(conn_id):
            await self._send_error(conn, "Rate limit exceeded")
            return
        try:
            payload = json.loads(raw)
            event_str = payload.get("event")
            data = payload.get("data", {})
            event = EventType(event_str) if event_str else None
            if not event:
                await self._send_error(conn, "Invalid event type")
                return
            message = WebSocketMessage(event=event, data=data, room_id=payload.get("room_id"), user_id=conn.user_id)
            conn.update_heartbeat()
            for handler in self.handlers.get(event, []):
                try:
                    await handler(message)
                except Exception as exc:
                    logger.error("ws_handler_error", conn_id=conn_id, event=event.value, error=str(exc))
        except json.JSONDecodeError:
            await self._send_error(conn, "Invalid JSON payload")

    async def _send_error(self, conn: ConnectionInfo, error: str) -> None:
        try:
            await conn.websocket.send_json(WebSocketMessage(event=EventType.ERROR, data={"error": error}).to_dict())
        except Exception:
            pass

    async def _heartbeat_loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                now = datetime.now(timezone.utc)
                dead_connections = []
                for conn_id, conn in list(self.connections.items()):
                    if (now - conn.last_heartbeat).total_seconds() > self.heartbeat_timeout:
                        dead_connections.append(conn_id)
                for conn_id in dead_connections:
                    logger.info("ws_heartbeat_timeout", conn_id=conn_id)
                    await self.disconnect(conn_id)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("ws_heartbeat_error", error=str(exc))

    def get_stats(self) -> dict[str, Any]:
        return {
            "total_connections": len(self.connections),
            "authenticated_connections": sum(1 for c in self.connections.values() if c.user_id is not None),
            "total_rooms": len(self.room_subscriptions),
            "total_users_online": len(self.user_connections),
        }
