import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_api_key_required():
    # Без ключа
    response = client.get(f"{settings.API_V1_STR}/dictionaries/regions")
    assert response.status_code == 403
    assert "Ключ доступа не предоставлен" in response.json()["detail"]

def test_invalid_api_key():
    response = client.get(
        f"{settings.API_V1_STR}/dictionaries/accident-types",
        headers={"X-API-KEY": "invalid_key_that_is_long_enough_to_pass_validation"}
    )
    assert response.status_code == 403
    # Проверка нового текста ошибки
    assert response.json()["detail"] == "Некорректный или неактивный ключ доступа"
