from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to DTP Analytics API" in response.json()["message"]

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": settings.VERSION}

def test_api_key_required():
    # Эндпоинты под роутером требуют API ключ
    response = client.get(f"{settings.API_V1_STR}/dictionaries/accident-types")
    assert response.status_code == 403
    assert response.json()["detail"] == "Ключ доступа не предоставлен"

def test_invalid_api_key():
    response = client.get(
        f"{settings.API_V1_STR}/dictionaries/accident-types",
        headers={"X-API-KEY": "invalid_key_that_is_long_enough_to_pass_validation_if_it_was_checked_here"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Некорректный ключ доступа"
