from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.schemas.admin import AdminUserSearch
from app.services import AdminService, DepositService, WithdrawalService, WalletService
from app.services.telegram_bot_service import telegram_bot

router = APIRouter()


@router.get("/bot/commands")
async def get_bot_commands() -> dict[str, Any]:
    return {"commands": telegram_bot.get_commands()}


@router.post("/bot/notify/{user_id}")
async def notify_user(user_id: UUID, title: str, body: str, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    wallet_service = WalletService(db)
    user = await wallet_service.user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    payload = telegram_bot.build_announcement(title, body)
    payload["chat_id"] = user.telegram_id
    return {"status": "queued", "payload": payload}


@router.post("/bot/broadcast")
async def broadcast_announcement(title: str, body: str) -> dict[str, str]:
    payload = telegram_bot.build_announcement(title, body)
    return {"status": "queued", "payload": payload}


@router.post("/bot/winner/{game_id}")
async def notify_winner(game_id: UUID, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    from app.models.models import Game
    from app.repositories import GameRepository
    game_repo = GameRepository(db)
    game = await game_repo.get_by_id(game_id)
    if not game or not game.winner_id:
        raise HTTPException(status_code=404, detail="Game or winner not found")
    user = await WalletService(db).user_repo.get_by_id(game.winner_id)
    if not user:
        raise HTTPException(status_code=404, detail="Winner not found")
    payload = telegram_bot.build_winner_notification(user.username or user.first_name or "Player", game.prize_amount or 0, str(game.id))
    payload["chat_id"] = user.telegram_id
    return {"status": "queued", "payload": payload}
