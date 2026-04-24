import hashlib
import hmac
import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.db.session import engine, Base
from app.services import auth as auth_service

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Создание таблиц в БД перед запуском тестов модуля."""
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    asyncio.run(create_tables())
    yield

def test_auth_flow():
    """
    Верификация новой системы авторизации:
    1. Запрос POST /api/v1/auth/keys с корректным X-MASTER-KEY.
    2. Сохранение полученного access_key.
    3. Запрос GET /api/v1/analytics/summary с этим ключом (ожидаем 200).
    4. Запрос с неверным ключом (ожидаем 403).
    """
    # 1. Запрос POST /api/v1/auth/keys с корректным X-MASTER-KEY
    master_key = settings.X_API_KEY.get_secret_value()
    response = client.post(
        f"{settings.API_V1_STR}/auth/keys",
        headers={"X-MASTER-KEY": master_key},
        json={"owner_name": "Test User"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_key" in data
    access_key = data["access_key"]
    
    # 2. Запрос GET /api/v1/analytics/summary с этим ключом (ожидаем 200)
    response = client.get(
        f"{settings.API_V1_STR}/analytics/summary",
        headers={"X-API-KEY": access_key}
    )
    assert response.status_code == 200
    
    # 3. Запрос с неверным ключом (ожидаем 403)
    response = client.get(
        f"{settings.API_V1_STR}/analytics/summary",
        headers={"X-API-KEY": "invalid_key"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Некорректный или неактивный ключ доступа"

def test_auth_invalid_master_key():
    """Проверка неверного Master-Key"""
    response = client.post(
        f"{settings.API_V1_STR}/auth/keys",
        headers={"X-MASTER-KEY": "wrong_master_key"},
        json={"owner_name": "Test User"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Неверный Master-Key"

def test_hash_key_uses_auth_salt():
    expected_hash = hmac.new(
        settings.AUTH_SALT.get_secret_value().encode("utf-8"),
        b"student_key_for_hashing",
        hashlib.sha256,
    ).hexdigest()

    assert auth_service.hash_key("student_key_for_hashing") == expected_hash
    assert auth_service.validate_key("student_key_for_hashing", expected_hash)
