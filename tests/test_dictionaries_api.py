import pytest
from fastapi.testclient import TestClient
from app.main import app, verify_api_key

@pytest.fixture(autouse=True)
def run_around_tests():
    async def override_verify_api_key():
        return "test_key"
    app.dependency_overrides[verify_api_key] = override_verify_api_key
    yield
    app.dependency_overrides.clear()

client = TestClient(app)

def test_get_regions():
    response = client.get("/api/v1/dictionaries/regions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_indicators():
    response = client.get("/api/v1/dictionaries/indicators")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_weather():
    response = client.get("/api/v1/dictionaries/weather")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_road_conditions():
    response = client.get("/api/v1/dictionaries/road-conditions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_accident_types():
    response = client.get("/api/v1/dictionaries/accident-types")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
