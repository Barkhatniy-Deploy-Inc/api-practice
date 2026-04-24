import hashlib
import hmac
import secrets

from app.core.config import settings

def generate_new_key() -> str:
    """
    Генерирует новый API ключ.
    Использует secrets.token_urlsafe(32) для создания криптографически стойкого ключа.
    """
    return secrets.token_urlsafe(32)

def hash_key(key: str) -> str:
    """
    Возвращает HMAC-SHA256 хеш ключа с использованием AUTH_SALT.
    """
    return hmac.new(
        settings.AUTH_SALT.get_secret_value().encode("utf-8"),
        key.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

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
