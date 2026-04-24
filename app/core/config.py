from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Зебра-стат — Аналитика ДТП"
    PROJECT_DESCRIPTION: str = "API для анализа данных о дорожно-транспортных происшествиях (ДТП). Предоставляет инструменты для работы со справочниками, данными о происшествиях и аналитическими отчетами."
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    X_API_KEY: SecretStr
    AUTH_SALT: SecretStr
    
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

    @field_validator("AUTH_SALT", mode="after")
    @classmethod
    def validate_auth_salt(cls, v: SecretStr) -> SecretStr:
        if len(v.get_secret_value()) < 16:
            raise ValueError("AUTH_SALT должен быть не менее 16 символов для стабильного хеширования")
        return v

settings = Settings()
