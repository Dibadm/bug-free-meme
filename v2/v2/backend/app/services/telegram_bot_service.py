from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class TelegramBotService:
    def __init__(self) -> None:
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.web_app_url = settings.TELEGRAM_WEB_APP_URL
        self._commands: dict[str, dict[str, Any]] = {}

    def register_command(self, command: str, description: str, handler: str) -> None:
        self._commands[command] = {"description": description, "handler": handler}

    def get_commands(self) -> list[dict[str, str]]:
        return [{"command": cmd, "description": info["description"]} for cmd, info in self._commands.items()]

    def build_start_message(self, user_name: str = "Player") -> dict[str, Any]:
        return {
            "chat_id": None,
            "text": f"Welcome {user_name}! 🎱\n\nPlay premium bingo and win big.\nTap the button below to launch the game.",
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "🎱 Play Bingo", "web_app": {"url": self.web_app_url}}]
                ]
            },
        }

    def build_help_message(self) -> dict[str, Any]:
        lines = ["<b>Commands</b>"]
        for cmd, info in self._commands.items():
            lines.append(f"/{cmd} - {info['description']}")
        return {
            "chat_id": None,
            "text": "\n".join(lines),
            "parse_mode": "HTML",
        }

    def build_profile_message(self, username: str, balance: float, games_played: int) -> dict[str, Any]:
        return {
            "chat_id": None,
            "text": f"<b>Profile</b>\n\nUsername: {username}\nBalance: {balance:.2f} ETB\nGames Played: {games_played}",
            "parse_mode": "HTML",
        }

    def build_wallet_message(self, balance: float, bonus: float, pending_deposit: float, pending_withdrawal: float) -> dict[str, Any]:
        return {
            "chat_id": None,
            "text": (
                f"<b>Wallet</b>\n\n"
                f"Balance: {balance:.2f} ETB\n"
                f"Bonus: {bonus:.2f} ETB\n"
                f"Pending Deposit: {pending_deposit:.2f} ETB\n"
                f"Pending Withdrawal: {pending_withdrawal:.2f} ETB"
            ),
            "parse_mode": "HTML",
        }

    def build_deposit_instructions(self) -> dict[str, Any]:
        return {
            "chat_id": None,
            "text": (
                "<b>Deposit</b>\n\n"
                "Send money to:\n"
                "Bank: Example Bank\n"
                "Account: 1234567890\n\n"
                "Then submit proof in the app."
            ),
            "parse_mode": "HTML",
        }

    def build_withdrawal_info(self, min_amount: float, fee: float) -> dict[str, Any]:
        return {
            "chat_id": None,
            "text": (
                f"<b>Withdraw</b>\n\n"
                f"Min: {min_amount:.2f} ETB\n"
                f"Fee: {fee:.2f} ETB\n\n"
                f"Use /withdraw to request."
            ),
            "parse_mode": "HTML",
        }

    def build_referral_message(self, code: str, link: str, earnings: float) -> dict[str, Any]:
        return {
            "chat_id": None,
            "text": (
                f"<b>Refer Friends</b>\n\n"
                f"Your code: <code>{code}</code>\n"
                f"Link: {link}\n"
                f"Total earnings: {earnings:.2f} ETB"
            ),
            "parse_mode": "HTML",
        }

    def build_support_message(self) -> dict[str, Any]:
        return {
            "chat_id": None,
            "text": "Need help? Contact @habeshabet_support",
        }

    def build_leaderboard_message(self, top_players: list[dict[str, Any]]) -> dict[str, Any]:
        lines = ["<b>Leaderboard</b>"]
        for idx, player in enumerate(top_players, start=1):
            lines.append(f"{idx}. {player.get('username', 'Unknown')} - {player.get('score', 0):.2f}")
        return {
            "chat_id": None,
            "text": "\n".join(lines),
            "parse_mode": "HTML",
        }

    def build_current_rooms_message(self, rooms: list[dict[str, Any]]) -> dict[str, Any]:
        if not rooms:
            return {"chat_id": None, "text": "No active rooms right now."}
        lines = ["<b>Current Rooms</b>"]
        for room in rooms[:10]:
            lines.append(f"- {room.get('name', 'Room')} ({room.get('status')})")
        return {
            "chat_id": None,
            "text": "\n".join(lines),
            "parse_mode": "HTML",
        }

    def build_history_message(self, history: list[dict[str, Any]]) -> dict[str, Any]:
        lines = ["<b>Recent Games</b>"]
        for item in history[:10]:
            lines.append(f"- {item.get('room_name')} | {item.get('result')}")
        return {
            "chat_id": None,
            "text": "\n".join(lines),
            "parse_mode": "HTML",
        }

    def build_settings_message(self, settings_data: dict[str, Any]) -> dict[str, Any]:
        return {
            "chat_id": None,
            "text": "<b>Settings</b>\n\nLanguage and preferences can be managed in the app.",
            "parse_mode": "HTML",
        }

    def build_winner_notification(self, username: str, prize: float, game_id: str) -> dict[str, Any]:
        return {
            "chat_id": None,
            "text": f"🎉 Winner!\n{username} won {prize:.2f} ETB in game {game_id}",
        }

    def build_deposit_approved(self, amount: float) -> dict[str, Any]:
        return {
            "chat_id": None,
            "text": f"✅ Deposit approved: {amount:.2f} ETB",
        }

    def build_withdrawal_approved(self, amount: float) -> dict[str, Any]:
        return {
            "chat_id": None,
            "text": f"✅ Withdrawal approved: {amount:.2f} ETB",
        }

    def build_maintenance_alert(self, message: str) -> dict[str, Any]:
        return {
            "chat_id": None,
            "text": f"🔧 Maintenance\n{message}",
        }

    def build_announcement(self, title: str, body: str) -> dict[str, Any]:
        return {
            "chat_id": None,
            "text": f"<b>{title}</b>\n\n{body}",
            "parse_mode": "HTML",
        }

    def build_daily_reward_reminder(self) -> dict[str, Any]:
        return {
            "chat_id": None,
            "text": "🎁 Don't forget to claim your daily reward!",
        }

    def build_referral_reward_notification(self, amount: float, referrer: str) -> dict[str, Any]:
        return {
            "chat_id": None,
            "text": f"🎉 You earned {amount:.2f} ETB from {referrer}'s referral!",
        }

    def build_admin_notification(self, message: str) -> dict[str, Any]:
        return {
            "chat_id": None,
            "text": f"🛠 Admin: {message}",
        }


telegram_bot = TelegramBotService()
for cmd in [
    ("start", "Start the bot", "handle_start"),
    ("help", "Show help", "handle_help"),
    ("profile", "View profile", "handle_profile"),
    ("wallet", "View wallet", "handle_wallet"),
    ("deposit", "Deposit info", "handle_deposit"),
    ("withdraw", "Withdraw info", "handle_withdraw"),
    ("referral", "Referral info", "handle_referral"),
    ("support", "Contact support", "handle_support"),
    ("leaderboard", "Leaderboard", "handle_leaderboard"),
    ("currentrooms", "Current rooms", "handle_currentrooms"),
    ("mygames", "My games", "handle_mygames"),
    ("history", "Game history", "handle_history"),
    ("settings", "Settings", "handle_settings"),
]:
    telegram_bot.register_command(cmd[0], cmd[1], cmd[2])
