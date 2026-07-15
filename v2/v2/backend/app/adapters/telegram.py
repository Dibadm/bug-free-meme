from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class TelegramAdapter:
    def __init__(self) -> None:
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.web_app_url = settings.TELEGRAM_WEB_APP_URL

    def build_web_app_button(self, text: str = "Play Bingo") -> dict[str, Any]:
        return {
            "inline_keyboard": [
                [
                    {
                        "text": text,
                        "web_app": {"url": self.web_app_url},
                    }
                ]
            ]
        }

    def validate_init_data(self, init_data: str) -> dict[str, Any]:
        import hashlib
        import hmac
        import json
        from urllib.parse import parse_qsl

        if not init_data:
            raise ValueError("Empty init data")

        parsed = dict(parse_qsl(init_data))
        hash_value = parsed.pop("hash", None)
        if not hash_value:
            raise ValueError("Missing hash")

        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
        secret_key = hashlib.sha256(self.bot_token.encode()).digest()
        expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected_hash, hash_value):
            raise ValueError("Invalid init data hash")

        return parsed

    def extract_user(self, init_data: dict[str, Any]) -> dict[str, Any]:
        user_str = init_data.get("user")
        if not user_str:
            raise ValueError("Missing user in init data")
        return json.loads(user_str)

telegram_adapter = TelegramAdapter()
