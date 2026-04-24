import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_health_check():
    """Проверка работоспособности системы"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "1.0.0"}

def test_auth_me_integration(auth_headers):
    """Проверка эндпоинта идентификации владельца ключа"""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert "owner_name" in response.json()

def test_analytics_summary_integration(auth_headers):
    """Проверка сводной статистики"""
    response = client.get("/api/v1/stats/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_accidents" in data
    assert "total_fatalities" in data

def test_hotspots_map_integration(auth_headers):
    """Проверка эндпоинта тепловой карты (SQL кластеризация)"""
    response = client.get("/api/v1/analytics/reports/hotspots-map", headers=auth_headers)
    assert response.status_code == 200
    assert "points" in response.json()

def test_participant_profile_integration(auth_headers):
    """Проверка портрета виновника (SQL агрегация)"""
    response = client.get("/api/v1/analytics/reports/participant-profile", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "gender" in data
    assert "age_group" in data
    assert "experience_group" in data

def test_unauthorized_access():
    """Проверка блокировки доступа без ключа"""
    response = client.get("/api/v1/stats/summary")
    assert response.status_code == 403
