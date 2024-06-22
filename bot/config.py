import sys

from pydantic_settings import BaseSettings
import logging


class Settings(BaseSettings):
    DEBUG: bool = False

    DISCORD_BOT_TOKEN: str
    SENTRY_DSN: str = ''

    REDIS_URL: str = 'redis://redis:6379'


settings = Settings(_env_file='.env')


logger = logging.getLogger('discord-bot')
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
