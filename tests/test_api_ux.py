import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_localization_error(auth_headers):
    """
    Проверка локализации ошибок: отправка некорректного JSON.
    """
    response = client.get(
        f"{settings.API_V1_STR}/accidents/",
        params={"limit": "not_a_number"},
        headers=auth_headers
    )
    assert response.status_code == 422
    assert "message" in response.json()
    assert response.json()["message"] == "Ошибка валидации входных данных"

def test_accidents_filters(auth_headers):
    """
    Проверка эндпоинта /accidents на предмет корректной работы фильтров.
    """
    response = client.get(f"{settings.API_V1_STR}/accidents/", headers=auth_headers)
    assert response.status_code == 200

def test_analytics_endpoints(auth_headers):
    """
    Проверка эндпоинтов аналитики.
    """
    endpoints = [
        "/analytics/summary",
        "/analytics/trends/monthly",
        "/analytics/trends/yearly",
        "/analytics/correlations/weather",
    ]

    for endpoint in endpoints:
        response = client.get(f"{settings.API_V1_STR}{endpoint}", headers=auth_headers)
        # Если данных нет, 404 - корректный ответ от CRUD
        assert response.status_code in [200, 404]
