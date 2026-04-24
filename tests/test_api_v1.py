import pytest
from fastapi.testclient import TestClient
from app.main import app, verify_api_key
from app.core.config import settings

@pytest.fixture(autouse=True)
def run_around_tests():
    # Отключаем проверку API-ключа для тестов этого файла
    async def override_verify_api_key():
        return "test_key"
    
    app.dependency_overrides[verify_api_key] = override_verify_api_key
    yield
    # Очищаем переопределения после завершения тестов файла
    app.dependency_overrides.clear()

client = TestClient(app)

def test_health_status_code():
    """Проверка статус-кода эндпоинта /health"""
    response = client.get("/health")
    assert response.status_code == 200

def test_summary_status_code():
    """Проверка статус-кода эндпоинта /api/v1/analytics/summary"""
    response = client.get(f"{settings.API_V1_STR}/analytics/summary")
    assert response.status_code == 200
