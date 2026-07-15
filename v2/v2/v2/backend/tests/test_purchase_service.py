from __future__ import annotations

import pytest
from uuid import uuid4

from app.core.exceptions import ValidationError
from app.services import PurchaseService


@pytest.mark.asyncio
async def test_purchase_cards(db_session: Any) -> None:
    from app.services import CardService, RoomTemplateService

    template_service = RoomTemplateService(db_session)
    template = await template_service.create_template(
        name="Template",
        entry_fee=10.0,
        max_players=10,
        min_players=2,
        winning_pattern="four_corners",
        house_percentage=Decimal("60.00"),
    )

    card_service = CardService(db_session)
    cards = await card_service.generate_cards(template.id, 3)
    assert len(cards) == 3

    purchase_service = PurchaseService(db_session)
    purchased = await purchase_service.purchase_cards(uuid4(), template.id, [cards[0].id, cards[1].id])
    assert len(purchased) == 2


@pytest.mark.asyncio
async def test_purchase_duplicate_card_fails(db_session: Any) -> None:
    from app.services import CardService, RoomTemplateService

    template_service = RoomTemplateService(db_session)
    template = await template_service.create_template(
        name="Template",
        entry_fee=10.0,
        max_players=10,
        min_players=2,
        winning_pattern="four_corners",
        house_percentage=Decimal("60.00"),
    )

    card_service = CardService(db_session)
    cards = await card_service.generate_cards(template.id, 2)
    purchase_service = PurchaseService(db_session)
    user_id = uuid4()
    await purchase_service.purchase_cards(user_id, template.id, [cards[0].id])
    with pytest.raises(ValidationError, match="already purchased"):
        await purchase_service.purchase_cards(user_id, template.id, [cards[0].id])


@pytest.mark.asyncio
async def test_mark_card(db_session: Any) -> None:
    from app.services import CardService, PurchaseService, RoomTemplateService

    template_service = RoomTemplateService(db_session)
    template = await template_service.create_template(
        name="Template",
        entry_fee=10.0,
        max_players=10,
        min_players=2,
        winning_pattern="four_corners",
        house_percentage=Decimal("60.00"),
    )

    card_service = CardService(db_session)
    cards = await card_service.generate_cards(template.id, 1)
    purchase_service = PurchaseService(db_session)
    purchased = await purchase_service.purchase_cards(uuid4(), template.id, [cards[0].id])
    marked = await purchase_service.mark_card(purchased[0].id, 42)
    assert 42 in (marked.marks or [])
