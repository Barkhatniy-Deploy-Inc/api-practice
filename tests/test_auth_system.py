import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings

@pytest.mark.asyncio
async def test_auth_flow(engine):
    """
    Верификация новой системы авторизации:
    1. Запрос POST /api/v1/auth/keys с корректным X-MASTER-KEY.
    2. Сохранение полученного access_key.
    3. Запрос GET /api/v1/analytics/summary с этим ключом (ожидаем 200).
    4. Запрос с неверным ключом (ожидаем 403).
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Запрос POST /api/v1/auth/keys с корректным X-MASTER-KEY
        master_key = settings.X_API_KEY.get_secret_value()
        response = await client.post(
            f"{settings.API_V1_STR}/auth/keys",
            headers={"X-MASTER-KEY": master_key},
            json={"owner_name": "Test User"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_key" in data
        access_key = data["access_key"]
        
        # 2. Запрос GET /api/v1/analytics/summary с этим ключом (ожидаем 200)
        response = await client.get(
            f"{settings.API_V1_STR}/analytics/summary",
            headers={"X-API-KEY": access_key}
        )
        assert response.status_code == 200
        
        # 3. Запрос с неверным ключом (ожидаем 403)
        response = await client.get(
            f"{settings.API_V1_STR}/analytics/summary",
            headers={"X-API-KEY": "invalid_key"}
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Некорректный или неактивный ключ доступа"

@pytest.mark.asyncio
async def test_auth_invalid_master_key():
    """Проверка неверного Master-Key"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"{settings.API_V1_STR}/auth/keys",
            headers={"X-MASTER-KEY": "wrong_master_key"},
            json={"owner_name": "Test User"}
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Неверный Master-Key"
