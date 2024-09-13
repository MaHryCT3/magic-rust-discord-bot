import logging

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from core.logger import logger


class Settings(BaseSettings):
    model_config = ConfigDict(extra='ignore')
    DEBUG: bool = False

    REDIS_URL: str


settings = Settings(_env_file='.env')
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
