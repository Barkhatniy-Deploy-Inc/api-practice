import secrets
import hashlib

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
    return hashlib.sha256(key.encode()).hexdigest()

def get_key_prefix(key: str) -> str:
    """
    Возвращает префикс ключа (первые 8 символов).
    """
    return key[:8]

def validate_key(key: str, hashed_key: str) -> bool:
    """
    Сравнивает хеш присланного ключа с хешем из БД.
    """
    return hash_key(key) == hashed_key
