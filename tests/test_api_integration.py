import pytest
from fastapi.testclient import TestClient
from app.main import app, verify_api_key

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

def test_health_check():
    """Проверка работоспособности системы"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_analytics_summary():
    """Проверка эндпоинта сводной статистики"""
    response = client.get("/api/v1/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_accidents" in data
    assert "total_fatalities" in data
    assert "total_injured" in data
    assert isinstance(data["total_accidents"], int)

def test_analytics_regions():
    """Проверка эндпоинта статистики по регионам"""
    response = client.get("/api/v1/analytics/regions")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 0
    if len(data["items"]) > 0:
        item = data["items"][0]
        assert "name" in item
        assert "code" in item
        assert "accidents" in item

def test_analytics_seasonality():
    """Проверка эндпоинта сезонности"""
    response = client.get("/api/v1/analytics/seasonality")
    # Если данных нет, может вернуть 404, но мы ожидаем 200 если БД не пуста
    if response.status_code == 200:
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 4
        for item in data["items"]:
            assert "season" in item
            assert "average_accidents" in item
    elif response.status_code == 404:
        assert response.json()["detail"] == "Нет данных для анализа сезонности"

def test_analytics_participant_profile():
    """Проверка эндпоинта портрета виновника"""
    response = client.get("/api/v1/analytics/reports/participant-profile")
    assert response.status_code == 200
    data = response.json()
    assert "gender" in data
    assert "age_group" in data
    assert "experience_group" in data
    assert "total_culprits" in data
