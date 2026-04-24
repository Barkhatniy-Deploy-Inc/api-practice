from datetime import datetime
from pydantic import BaseModel, ConfigDict

class APIKeyCreate(BaseModel):
    """Схема для создания API ключа"""
    owner_name: str

class APIKeyResponse(BaseModel):
    """Схема для отображения метаданных API ключа"""
    id: int
    owner_name: str
    prefix: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class APIKeyGenerated(APIKeyResponse):
    """Схема ответа при генерации нового ключа (содержит сырой ключ)"""
    access_key: str
