from fastapi import APIRouter

from app.api.v1 import admin, auth, bot, games, payment_settings, rooms, wallet
from app.api.v1 import websocket as ws_router

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(bot.router, prefix="/bot", tags=["bot"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
api_router.include_router(wallet.router, prefix="/wallet", tags=["wallet"])
api_router.include_router(payment_settings.router, prefix="/payment-settings", tags=["payment-settings"])
api_router.include_router(ws_router.router, prefix="/ws", tags=["websocket"])

