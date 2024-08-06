import logging
import sys
from datetime import timedelta, timezone

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = False
    TIMEZONE: timezone = timezone(offset=timedelta(hours=3), name='Europe/Moscow')

    DISCORD_BOT_TOKEN: str
    SENTRY_DSN: str = ''

    REDIS_URL: str = 'redis://localhost:6379'
    SERVER_API_URL: str


settings = Settings(_env_file='.env')


logger = logging.getLogger('discord-bot')
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
