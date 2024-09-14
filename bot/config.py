import logging
from datetime import timedelta, timezone

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from core.logger import logger


class Settings(BaseSettings):
    model_config = ConfigDict(extra='ignore')

    DEBUG: bool = False
    SENTRY_DSN: str = ''
    TIMEZONE: timezone = timezone(offset=timedelta(hours=3), name='Europe/Moscow')

    DISCORD_MAIN_BOT_TOKEN: str
    DISCORD_OWNER_IDS: list[int]
    MAGIC_RUST_GUILD_ID: str

    VK_MAIN_GROUP_TOKEN: str
    VK_MAIN_GROUP_ID: int
    REPORT_VK_BOT_TOKEN: str

    REDIS_URL: str = 'redis://localhost:6379'
    SETUP_APPS: list[str] | None = None


settings = Settings(_env_file='.env')


logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
