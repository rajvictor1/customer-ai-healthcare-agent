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
    CORS_ORIGINS: str = "http://localhost:8000,http://127.0.0.1:8000"
    PHI_INTEGRATIONS_ENABLED: bool = False
    FHIR_API_BASE_URL: str = ""
    FHIR_API_TOKEN: str = ""
    SCHEDULING_API_BASE_URL: str = ""
    SCHEDULING_API_TOKEN: str = ""
    PHARMACY_API_BASE_URL: str = ""
    PHARMACY_API_TOKEN: str = ""
    BILLING_API_BASE_URL: str = ""
    BILLING_API_TOKEN: str = ""
    PROVIDER_DIRECTORY_API_BASE_URL: str = ""
    PROVIDER_DIRECTORY_API_TOKEN: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

@lru_cache()
def get_settings():
    return Settings()
