import secrets
import hashlib
from app.core.config import settings

def generate_new_key() -> str:
    """
    Генерирует новый API ключ.
    Использует secrets.token_urlsafe(32) для создания криптографически стойкого ключа.
    """
    return secrets.token_urlsafe(32)

def hash_key(key: str) -> str:
    """
    Возвращает SHA-256 хеш ключа.
    """
    salted_key = f"{settings.AUTH_SALT}{key}"
    return hashlib.sha256(salted_key.encode()).hexdigest()

def get_key_prefix(key: str) -> str:
    """
    Возвращает префикс ключа (первые 8 символов).
    """
    return key[:8]

def validate_key(key: str, hashed_key: str) -> bool:
    """
    Сравнивает хеш присланного ключа с хешем из БД.
    """
    return secrets.compare_digest(hash_key(key), hashed_key)
