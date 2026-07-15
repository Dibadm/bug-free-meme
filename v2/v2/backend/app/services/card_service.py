from __future__ import annotations

from typing import Any
from uuid import UUID

from app.core.exceptions import ValidationError
from app.models.models import Card, RoomStatus
from app.repositories import CardRepository, RoomRepository
from app.services.base import BaseService


class CardService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.card_repo = CardRepository(db)
        self.room_repo = RoomRepository(db)

    async def generate_cards(self, room_id: UUID, count: int) -> list[Card]:
        room = await self.room_repo.get_by_id(room_id)
        if not room:
            raise ValidationError("Room not found")
        if room.status not in (RoomStatus.WAITING, RoomStatus.OPEN):
            raise ValidationError("Room is not accepting card purchases")

        cards = []
        for _ in range(count):
            card = Card(room_id=room_id, numbers=[], pattern_index=0)
            await self.card_repo.create(card)
            cards.append(card)
        return cards

    async def get_room_cards(self, room_id: UUID) -> list[Card]:
        return await self.card_repo.get_by_room_id(room_id)

    async def get_available_cards(self, room_id: UUID, limit: int = 50) -> list[Card]:
        return await self.card_repo.get_available_cards(room_id, limit=limit)
