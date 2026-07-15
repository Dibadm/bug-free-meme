from __future__ import annotations

import pytest

from app.services.telegram_bot_service import telegram_bot


class TestTelegramBotService:
    def test_register_command(self) -> None:
        telegram_bot.register_command("test", "Test command", "handle_test")
        commands = telegram_bot.get_commands()
        assert any(cmd["command"] == "test" for cmd in commands)

    def test_build_start_message(self) -> None:
        message = telegram_bot.build_start_message("Habesha")
        assert message["text"].startswith("Welcome Habesha")
        assert message["reply_markup"] is not None

    def test_build_help_message(self) -> None:
        message = telegram_bot.build_help_message()
        assert "Commands" in message["text"]
        assert message["parse_mode"] == "HTML"

    def test_build_profile_message(self) -> None:
        message = telegram_bot.build_profile_message("user1", 100.5, 10)
        assert "user1" in message["text"]
        assert "100.50" in message["text"]

    def test_build_wallet_message(self) -> None:
        message = telegram_bot.build_wallet_message(100.0, 10.0, 50.0, 20.0)
        assert "100.00" in message["text"]
        assert "10.00" in message["text"]

    def test_build_winner_notification(self) -> None:
        message = telegram_bot.build_winner_notification("Player1", 500.0, "game-1")
        assert "Player1" in message["text"]
        assert "500.00" in message["text"]

    def test_build_maintenance_alert(self) -> None:
        message = telegram_bot.build_maintenance_alert("System upgrade")
        assert "System upgrade" in message["text"]

    def test_build_announcement(self) -> None:
        message = telegram_bot.build_announcement("Title", "Body")
        assert "Title" in message["text"]
        assert "Body" in message["text"]
