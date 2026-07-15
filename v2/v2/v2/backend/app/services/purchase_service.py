from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from app.core.exceptions import ValidationError
from app.models.models import PurchasedCard, WalletTransactionType
from app.repositories import PurchasedCardRepository, WalletRepository
from app.services.base import BaseService


class PurchaseService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.purchased_card_repo = PurchasedCardRepository(db)
        self.wallet_repo = WalletRepository(db)

    async def purchase_cards(self, user_id: UUID, game_id: UUID, card_ids: list[UUID]) -> list[PurchasedCard]:
        if not card_ids:
            raise ValidationError("No cards selected")

        existing = await self.purchased_card_repo.get_by_user_and_game(user_id, game_id)
        existing_card_ids = {pc.card_id for pc in existing}
        duplicate_ids = set(card_ids) & existing_card_ids
        if duplicate_ids:
            raise ValidationError("Some cards are already purchased")

        purchased = []
        for card_id in card_ids:
            purchased_card = PurchasedCard(
                game_id=game_id,
                card_id=card_id,
                user_id=user_id,
                purchased_at=datetime.now(timezone.utc),
            )
            await self.purchased_card_repo.create(purchased_card)
            purchased.append(purchased_card)
        return purchased

    async def mark_card(self, purchased_card_id: UUID, number: int) -> PurchasedCard | None:
        purchased = await self.purchased_card_repo.get_by_id(purchased_card_id)
        if not purchased:
            return None
        marks = purchased.marks or []
        if number not in marks:
            marks.append(number)
            purchased.marks = marks
            await self.db.flush()
            await self.db.refresh(purchased)
        return purchased

    async def get_user_cards(self, user_id: UUID, game_id: UUID) -> list[PurchasedCard]:
        return await self.purchased_card_repo.get_by_user_and_game(user_id, game_id)
