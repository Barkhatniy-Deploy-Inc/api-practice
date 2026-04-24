from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.db.session import Base

class APIKey(Base):
    """Модель API ключа для аутентификации"""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_name = Column(String, nullable=False)
    key_hash = Column(String, index=True, nullable=False)
    prefix = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
