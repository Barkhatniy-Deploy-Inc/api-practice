from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
import sys

client = TestClient(app)
# Используем ключ прямо из настроек, чтобы тест прошел независимо от того, что в .env
API_KEY = settings.X_API_KEY.get_secret_value()
HEADERS = {"X-API-KEY": API_KEY}

def test_endpoint(path, params=None):
    print(f"Testing {path} with params {params}...")
    response = client.get(f"{settings.API_V1_STR}{path}", params=params, headers=HEADERS)
    if response.status_code == 200:
        print(f"SUCCESS: {path}")
        return True
    else:
        print(f"FAILED: {path} - Status: {response.status_code}, Detail: {response.json()}")
        return False

if __name__ == "__main__":
    all_passed = True
    all_passed &= test_endpoint("/analytics/summary")
    all_passed &= test_endpoint("/analytics/regions")
    all_passed &= test_endpoint("/analytics/timeline")
    all_passed &= test_endpoint("/analytics/timeline", {"interval": "day"})
    all_passed &= test_endpoint("/analytics/timeline", {"interval": "year"})
    all_passed &= test_endpoint("/analytics/regions", {"sort_by": "fatalities", "order": "asc"})
    
    if not all_passed:
        sys.exit(1)
