from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(extra='ignore')
    SERVER_API_URL: str
    REDIS_URL: str

settings = Settings(_env_file='.env')