from __future__ import annotations

from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.websocket.auth import authenticate_connection
from app.websocket.channels import AdminChannel, RoomChannel, UserChannel
from app.websocket.events import EventType
from app.websocket.manager import ws_manager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str | None = None, db: AsyncSession = Depends(get_db)) -> None:
    user_id = None
    device_info = websocket.headers.get("user-agent", "")
    conn_id = await ws_manager.connect(websocket, user_id=None, token=token, device_info=device_info)
    try:
        if token:
            auth_result = await authenticate_connection(ws_manager.connections[conn_id], db)
            if not auth_result:
                return
            user_id = ws_manager.connections[conn_id].user_id

        await UserChannel.send(
            user_id,
            EventType.CONNECTION_STATE,
            {"status": "connected", "conn_id": conn_id},
        )

        while True:
            data = await websocket.receive_text()
            await ws_manager.handle_message(conn_id, data)
    except WebSocketDisconnect:
        pass
    finally:
        await ws_manager.disconnect(conn_id)
        if user_id:
            await UserChannel.send(user_id, EventType.CONNECTION_STATE, {"status": "disconnected"})


@router.websocket("/ws/room/{room_id}")
async def websocket_room_endpoint(websocket: WebSocket, room_id: str, token: str | None = None, db: AsyncSession = Depends(get_db)) -> None:
    user_id = None
    device_info = websocket.headers.get("user-agent", "")
    conn_id = await ws_manager.connect(websocket, user_id=None, token=token, device_info=device_info)
    try:
        if token:
            auth_result = await authenticate_connection(ws_manager.connections[conn_id], db)
            if not auth_result:
                return
            user_id = ws_manager.connections[conn_id].user_id

        await ws_manager.subscribe_room(conn_id, room_id)
        await RoomChannel.publish(room_id, EventType.PLAYER_JOINED, {"user_id": str(user_id) if user_id else None, "conn_id": conn_id})

        while True:
            data = await websocket.receive_text()
            await ws_manager.handle_message(conn_id, data)
    except WebSocketDisconnect:
        pass
    finally:
        await ws_manager.unsubscribe_room(conn_id, room_id)
        await ws_manager.disconnect(conn_id)
        if user_id:
            await RoomChannel.publish(room_id, EventType.PLAYER_LEFT, {"user_id": str(user_id)})


@router.websocket("/ws/admin")
async def websocket_admin_endpoint(websocket: WebSocket, token: str | None = None, db: AsyncSession = Depends(get_db)) -> None:
    conn_id = await ws_manager.connect(websocket, user_id=None, token=token, device_info=websocket.headers.get("user-agent", ""))
    try:
        if token:
            auth_result = await authenticate_connection(ws_manager.connections[conn_id], db)
            if not auth_result:
                return
            user_id = ws_manager.connections[conn_id].user_id
            from app.models.models import UserRole
            from app.services.auth_service import AuthService
            auth_service = AuthService(db)
            user = await auth_service.user_repo.get_by_id(user_id)
            if not user or user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
                await websocket.close(code=4003)
                return
        else:
            await websocket.close(code=4001)
            return

        while True:
            data = await websocket.receive_text()
            await ws_manager.handle_message(conn_id, data)
    except WebSocketDisconnect:
        pass
    finally:
        await ws_manager.disconnect(conn_id)
