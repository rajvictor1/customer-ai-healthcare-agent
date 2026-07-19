from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///data/conversations.db"
    SECRET_KEY: str = "change-me"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    AUTH_ISSUER: str = ""
    AUTH_CLIENT_ID: str = ""
    AUTH_CLIENT_SECRET: str = ""
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_NUMBER: str = ""
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
