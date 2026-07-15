from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Habesha Bet V2"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"

    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEB_APP_URL: str
    TELEGRAM_SECRET_TOKEN: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    HOUSE_WALLET_ID: str

    ADMIN_IDS: list[int] = []

    CRYPT_SECRET_KEY: bytes
    CRYPT_ALGORITHM: str = "Fernet"

    GAME_ENGINE_HOST: str = "localhost"
    GAME_ENGINE_PORT: int = 8001


settings = Settings()
