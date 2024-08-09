import logging
import sys
from datetime import timedelta, timezone

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(extra="ignore")
    DEBUG: bool = False
    TIMEZONE: timezone = timezone(offset=timedelta(hours=3), name='Europe/Moscow')

    DISCORD_BOT_TOKEN: str
    MAGIC_RUST_GUILD_ID: str
    SENTRY_DSN: str = ''

    REDIS_URL: str = 'redis://localhost:6379'


settings = Settings(_env_file='.env')


logger = logging.getLogger('discord-bot')
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
