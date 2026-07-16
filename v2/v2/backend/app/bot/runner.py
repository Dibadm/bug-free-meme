#!/usr/bin/env python3
"""Telegram Bot Runner for Habesha Bet V2

This script runs the Telegram bot using python-telegram-bot v20+.
Can be run standalone, or imported asynchronously into a FastAPI lifespan context.
"""
from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager

from telegram import BotCommand, Update, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from app.core.config import settings
from app.core.logging import get_logger
from app.services.telegram_bot_service import telegram_bot

logger = get_logger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    if not user:
        return

    web_app_url = settings.TELEGRAM_WEB_APP_URL
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎱 Play Bingo", web_app=WebAppInfo(url=web_app_url))]
    ])

    await update.message.reply_text(
        f"Welcome {user.first_name}! 🎱\n\n"
        f"Play premium bingo and win big.\n"
        f"Tap the button below to launch the game.",
        reply_markup=keyboard,
    )
    logger.info("bot_start", user_id=user.id, username=user.username)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    commands = telegram_bot.get_commands()
    lines = ["<b>Available Commands</b>"]
    for cmd in commands:
        lines.append(f"/{cmd['command']} - {cmd['description']}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /profile command."""
    user = update.effective_user
    if not user:
        return

    from app.services import AuthService, WalletService
    from app.core.database import async_session_maker

    async with async_session_maker() as db:
        auth_service = AuthService(db)
        user_record = await auth_service.get_or_create_user({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
        })

        wallet_service = WalletService(db)
        balance = await wallet_service.get_balance(user_record.id)
        stats = user_record.statistics

    message = telegram_bot.build_profile_message(
        username=user.username or user.first_name or "Player",
        balance=float(balance),
        games_played=stats.games_played if stats else 0,
    )
    await update.message.reply_text(message["text"], parse_mode="HTML")


async def wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /wallet command."""
    user = update.effective_user
    if not user:
        return

    from app.services import AuthService, WalletService
    from app.core.database import async_session_maker

    async with async_session_maker() as db:
        auth_service = AuthService(db)
        user_record = await auth_service.get_or_create_user({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
        })

        wallet_service = WalletService(db)
        balance = await wallet_service.get_balance(user_record.id)
        bonus = float(user_record.wallet.bonus_balance) if user_record.wallet else 0.0

    message = telegram_bot.build_wallet_message(
        balance=float(balance),
        bonus=bonus,
        pending_deposit=0.0,
        pending_withdrawal=0.0,
    )
    await update.message.reply_text(message["text"], parse_mode="HTML")


async def deposit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /deposit command."""
    message = telegram_bot.build_deposit_instructions()
    await update.message.reply_text(message["text"], parse_mode="HTML")


async def withdraw_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /withdraw command."""
    message = telegram_bot.build_withdrawal_info(min_amount=50.0, fee=5.0)
    await update.message.reply_text(message["text"], parse_mode="HTML")


async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /referral command."""
    user = update.effective_user
    if not user:
        return

    from app.services import AuthService, ReferralService
    from app.core.database import async_session_maker

    async with async_session_maker() as db:
        auth_service = AuthService(db)
        user_record = await auth_service.get_or_create_user({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
        })

        referral_service = ReferralService(db)
        referrals = await referral_service.get_user_referrals(user_record.id)
        total_earned = sum(r.total_earned for r in referrals)

    link = f"https://t.me/{settings.TELEGRAM_BOT_USERNAME or 'habeshabet_bot'}?startapp={user_record.referral_code}"
    message = telegram_bot.build_referral_message(
        code=user_record.referral_code or "",
        link=link,
        earnings=float(total_earned),
    )
    await update.message.reply_text(message["text"], parse_mode="HTML")


async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /support command."""
    message = telegram_bot.build_support_message()
    await update.message.reply_text(message["text"])


async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /leaderboard command."""
    from app.services import LeaderboardService
    from app.core.database import async_session_maker

    async with async_session_maker() as db:
        service = LeaderboardService(db)
        top_players = await service.get_top_players(period="weekly", limit=10)

    message = telegram_bot.build_leaderboard_message([
        {"username": p.username or "Player", "score": float(p.score)}
        for p in top_players
    ])
    await update.message.reply_text(message["text"], parse_mode="HTML")


async def current_rooms_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /currentrooms command."""
    from app.services import RoomService
    from app.core.database import async_session_maker

    async with async_session_maker() as db:
        service = RoomService(db)
        rooms = await service.get_active_rooms()

    message = telegram_bot.build_current_rooms_message([
        {"name": r.name, "status": r.status.value}
        for r in rooms
    ])
    await update.message.reply_text(message["text"], parse_mode="HTML")


async def mygames_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /mygames command."""
    await update.message.reply_text("Your recent games will appear here.")


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /history command."""
    await update.message.reply_text("Your game history will appear here.")


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /settings command."""
    message = telegram_bot.build_settings_message({})
    await update.message.reply_text(message["text"], parse_mode="HTML")


async def post_init(application: Application) -> None:
    """Post-initialization: set bot commands."""
    commands = [BotCommand(cmd["command"], cmd["description"]) for cmd in telegram_bot.get_commands()]
    await application.bot.set_my_commands(commands)
    logger.info("bot_commands_set", commands=commands)


def build_application() -> Application:
    """Helper to build the PTB Application instance."""
    application = (
        Application.builder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("wallet", wallet_command))
    application.add_handler(CommandHandler("deposit", deposit_command))
    application.add_handler(CommandHandler("withdraw", withdraw_command))
    application.add_handler(CommandHandler("referral", referral_command))
    application.add_handler(CommandHandler("support", support_command))
    application.add_handler(CommandHandler("leaderboard", leaderboard_command))
    application.add_handler(CommandHandler("currentrooms", current_rooms_command))
    application.add_handler(CommandHandler("mygames", mygames_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("settings", settings_command))
    return application


async def start_bot() -> None:
    """Run the Telegram bot asynchronously inside an existing asyncio event loop."""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set. Background bot cannot start.")
        return

    logger.info("bot_starting_async", token_prefix=settings.TELEGRAM_BOT_TOKEN[:10])
    application = build_application()

    # Async initialization & start sequences
    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    
    logger.info("bot_started_async_polling")
    try:
        # Keep cooperative polling alive forever
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info("bot_stopping_async_polling")
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


def main() -> None:
    """Fallback block for manual/CLI execution."""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set")
        return

    application = build_application()
    logger.info("bot_starting_blocking", token_prefix=settings.TELEGRAM_BOT_TOKEN[:10])
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
