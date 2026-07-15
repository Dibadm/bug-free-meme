from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.core.exceptions import ValidationError
from app.models.models import Game, Room, RoomStatus, GameStatus
from app.repositories import RoomRepository, GameRepository, CardRepository
from app.services.base import BaseService


class RoomService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.room_repo = RoomRepository(db)
        self.game_repo = GameRepository(db)
        self.card_repo = CardRepository(db)

    async def create_room(self, template_id: UUID, name: str) -> Room:
        template = await self.room_repo.get_by_id(template_id)
        if not template:
            raise ValidationError("Room template not found")

        room = Room(template_id=template_id, name=name, status=RoomStatus.WAITING)
        return await self.room_repo.create(room)

    async def open_room(self, room_id: UUID) -> Room | None:
        room = await self.room_repo.get_by_id(room_id)
        if not room:
            return None
        if room.status != RoomStatus.WAITING:
            raise ValidationError("Room is not in waiting state")

        room.status = RoomStatus.OPEN
        await self.db.flush()
        await self.db.refresh(room)
        return room

    async def lock_room(self, room_id: UUID) -> Room | None:
        room = await self.room_repo.get_by_id(room_id)
        if not room:
            return None
        if room.status != RoomStatus.OPEN:
            raise ValidationError("Room is not open")

        room.status = RoomStatus.LOCKED
        await self.db.flush()
        await self.db.refresh(room)
        return room

    async def start_game(self, room_id: UUID) -> Game:
        room = await self.room_repo.get_by_id(room_id)
        if not room:
            raise ValidationError("Room not found")
        if room.status != RoomStatus.LOCKED:
            raise ValidationError("Room must be locked before starting")

        active_game = await self.game_repo.get_active_game_by_room(room_id)
        if active_game:
            raise ValidationError("Room already has an active game")

        game = Game(room_id=room_id, status=GameStatus.STARTING)
        await self.db.add(game)
        room.game_id = game.id
        room.status = RoomStatus.RUNNING
        game.status = GameStatus.RUNNING
        game.started_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(game)
        return game

    async def finish_game(self, room_id: UUID) -> Room | None:
        room = await self.room_repo.get_by_id(room_id)
        if not room:
            return None

        room.status = RoomStatus.FINISHED
        await self.db.flush()
        await self.db.refresh(room)
        return room

    async def schedule_pending_rooms(self) -> None:
        pass
