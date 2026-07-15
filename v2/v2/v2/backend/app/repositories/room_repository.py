from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select, func

from app.models.models import Room, RoomTemplate, RoomStatus, Game, Card, PurchasedCard, GameStatus
from app.repositories import BaseRepository


class RoomRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, Room)

    async def get_by_template_id(self, template_id: UUID) -> list[Room]:
        result = await self.db.execute(
            select(Room).where(Room.template_id == template_id, Room.deleted_at.is_(None))
        )
        return list(result.scalars().all())

    async def get_active_room_by_template(self, template_id: UUID) -> Room | None:
        result = await self.db.execute(
            select(Room).where(
                Room.template_id == template_id,
                Room.status == RoomStatus.ACTIVE,
                Room.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def increment_cards_sold(self, room_id: UUID, count: int = 1) -> None:
        room = await self.get_by_id(room_id)
        if room:
            room.cards_sold = (room.cards_sold or 0) + count
            await self.db.flush()

    async def increment_current_players(self, room_id: UUID, count: int = 1) -> None:
        room = await self.get_by_id(room_id)
        if room:
            room.current_players = (room.current_players or 0) + count
            await self.db.flush()

    async def add_prize_pool(self, room_id: UUID, amount: Decimal) -> None:
        room = await self.get_by_id(room_id)
        if room:
            room.prize_pool = (room.prize_pool or Decimal("0.00")) + amount
            await self.db.flush()

    async def soft_delete(self, entity: Room) -> Room:
        entity.deleted_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity


class GameRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, Game)

    async def get_by_room_id(self, room_id: UUID) -> list[Game]:
        result = await self.db.execute(
            select(Game).where(Game.room_id == room_id, Game.deleted_at.is_(None)).order_by(Game.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_active_game_by_room(self, room_id: UUID) -> Game | None:
        result = await self.db.execute(
            select(Game).where(
                Game.room_id == room_id,
                Game.status.in_([GameStatus.WAITING, GameStatus.STARTING, GameStatus.RUNNING, GameStatus.PAUSED, GameStatus.RECOVERED]),
                Game.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_finished_games_by_room(self, room_id: UUID, limit: int = 50) -> list[Game]:
        result = await self.db.execute(
            select(Game)
            .where(Game.room_id == room_id, Game.status == GameStatus.FINISHED, Game.deleted_at.is_(None))
            .order_by(Game.finished_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def soft_delete(self, entity: Game) -> Game:
        entity.deleted_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity


class CardRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, Card)

    async def get_by_room_id(self, room_id: UUID) -> list[Card]:
        result = await self.db.execute(
            select(Card).where(Card.room_id == room_id, Card.is_sold == False)
        )
        return list(result.scalars().all())

    async def get_available_cards(self, room_id: UUID, limit: int = 50) -> list[Card]:
        result = await self.db.execute(
            select(Card).where(Card.room_id == room_id, Card.is_sold == False).limit(limit)
        )
        return list(result.scalars().all())

    async def mark_as_sold(self, card_id: UUID) -> None:
        card = await self.get_by_id(card_id)
        if card:
            card.is_sold = True
            await self.db.flush()

    async def count_sold_by_room(self, room_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count()).where(Card.room_id == room_id, Card.is_sold == True)
        )
        return result.scalar_one() or 0


class PurchasedCardRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, PurchasedCard)

    async def get_by_game_id(self, game_id: UUID) -> list[PurchasedCard]:
        result = await self.db.execute(
            select(PurchasedCard).where(PurchasedCard.game_id == game_id)
        )
        return list(result.scalars().all())

    async def get_by_user_and_game(self, user_id: UUID, game_id: UUID) -> list[PurchasedCard]:
        result = await self.db.execute(
            select(PurchasedCard).where(PurchasedCard.user_id == user_id, PurchasedCard.game_id == game_id)
        )
        return list(result.scalars().all())

    async def get_winner_cards(self, game_id: UUID) -> list[PurchasedCard]:
        result = await self.db.execute(
            select(PurchasedCard).where(PurchasedCard.game_id == game_id, PurchasedCard.is_winner == True)
        )
        return list(result.scalars().all())

    async def count_by_game(self, game_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count()).where(PurchasedCard.game_id == game_id)
        )
        return result.scalar_one() or 0
