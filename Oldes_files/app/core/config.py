from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    secret_key: str = Field("dev-secret-change-me", alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    database_url: str = Field(..., alias="DATABASE_URL")

    class Config:
        env_file = ".env"

settings = Settings()
