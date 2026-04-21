from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)
api_key = settings.X_API_KEY.get_secret_value()
headers = {"X-API-KEY": api_key}

def test_localization_error():
    """
    Проверка локализации ошибок: отправка некорректного JSON.
    """
    # Отправляем строку вместо числа в поле limit
    response = client.get(
        f"{settings.API_V1_STR}/accidents/",
        params={"limit": "not_a_number"},
        headers=headers
    )
    
    assert response.status_code == 422
    data = response.json()
    
    # Проверяем наличие сообщения на русском языке
    assert "message" in data
    assert data["message"] == "Ошибка валидации входных данных"
    
    # Проверяем детализацию ошибок
    assert "detail" in data
    found_russian = False
    for error in data["detail"]:
        if "Значение должно быть целым числом" in error["message"]:
            found_russian = True
            break
    
    assert found_russian, f"Russian error message not found in: {data['detail']}"

def test_accidents_filters():
    """
    Проверка эндпоинта /accidents на предмет корректной работы фильтров.
    """
    # Проверка базового запроса
    response = client.get(f"{settings.API_V1_STR}/accidents/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data

    # Проверка фильтра по региону (даже если данных нет, 200 OK ожидается)
    response = client.get(
        f"{settings.API_V1_STR}/accidents/",
        params={"region_code": "77"},
        headers=headers
    )
    assert response.status_code == 200

def test_analytics_endpoints():
    """
    Проверка эндпоинтов аналитики.
    """
    endpoints = [
        "/analytics/trends/monthly",
        "/analytics/trends/yearly",
        "/analytics/trends/prediction",
        "/analytics/correlations/weather",
        "/analytics/correlations/experience",
        "/analytics/correlations/lighting",
    ]
    
    for endpoint in endpoints:
        response = client.get(f"{settings.API_V1_STR}{endpoint}", headers=headers)
        # Если данных мало, может быть 404, что тоже корректно для логики
        assert response.status_code in [200, 404], f"Endpoint {endpoint} failed with {response.status_code}"

if __name__ == "__main__":
    # Если pytest не установлен, можно запустить этот файл напрямую для базовой проверки
    try:
        test_localization_error()
        print("test_localization_error: PASSED")
        test_accidents_filters()
        print("test_accidents_filters: PASSED")
        test_analytics_endpoints()
        print("test_analytics_endpoints: PASSED")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
