from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SERVER_API_URL: str

settings = Settings(_env_file='image_generator/.env')