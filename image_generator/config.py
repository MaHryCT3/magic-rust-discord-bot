import logging
import sys

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(extra='ignore')
    DEBUG: bool = False

    REDIS_URL: str


settings = Settings(_env_file='.env')
logger = logging.getLogger('image-generator')
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
