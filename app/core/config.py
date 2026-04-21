from typing import List, Union
from pydantic import AnyHttpUrl, field_validator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "DTP Analytics API"
    PROJECT_DESCRIPTION: str = "API для анализа данных о дорожно-транспортных происшествиях (ДТП). Предоставляет инструменты для работы со справочниками, данными о происшествиях и аналитическими отчетами."
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    X_API_KEY: SecretStr
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./dtp.db"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    DEBUG_MODE: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("X_API_KEY", mode="after")
    @classmethod
    def validate_api_key(cls, v: SecretStr) -> SecretStr:
        if len(v.get_secret_value()) < 32:
            raise ValueError("X_API_KEY должен быть не менее 32 символов для безопасности")
        return v

settings = Settings()
