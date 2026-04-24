import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_accidents_pagination_and_params(auth_headers):
    # Тест на покрытие эндпоинтов в app/api/v1/endpoints/accidents.py
    response = client.get(
        f"{settings.API_V1_STR}/accidents/",
        params={
            "limit": 10,
            "offset": 0,
            "has_children": True,
            "has_drunk": False
        },
        headers=auth_headers
    )
    assert response.status_code == 200

def test_analytics_extra_params(auth_headers):
    # Тест на покрытие фильтров в аналитике
    response = client.get(
        f"{settings.API_V1_STR}/analytics/regions",
        params={"sort_by": "fatalities", "order": "asc"},
        headers=auth_headers
    )
    assert response.status_code == 200
    
    response = client.get(
        f"{settings.API_V1_STR}/analytics/timeline",
        params={"interval": "year"},
        headers=auth_headers
    )
    assert response.status_code == 200

def test_auth_admin_key_list(master_headers):
    # Тест на покрытие GET /auth/keys
    response = client.get(f"{settings.API_V1_STR}/auth/keys", headers=master_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
