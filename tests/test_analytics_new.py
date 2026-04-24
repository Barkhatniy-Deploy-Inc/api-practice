import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_get_summary(auth_headers):
    response = client.get(f"{settings.API_V1_STR}/analytics/summary", headers=auth_headers)
    assert response.status_code == 200

def test_get_regions(auth_headers):
    response = client.get(f"{settings.API_V1_STR}/analytics/regions", headers=auth_headers)
    assert response.status_code == 200

def test_get_timeline(auth_headers):
    response = client.get(f"{settings.API_V1_STR}/analytics/timeline", headers=auth_headers)
    assert response.status_code == 200

def test_get_timeline_with_params(auth_headers):
    for interval in ["day", "month", "year"]:
        response = client.get(
            f"{settings.API_V1_STR}/analytics/timeline",
            params={"interval": interval},
            headers=auth_headers
        )
        assert response.status_code == 200

def test_get_regions_sorting(auth_headers):
    for sort_by in ["accidents", "fatalities"]:
        for order in ["asc", "desc"]:
            response = client.get(
                f"{settings.API_V1_STR}/analytics/regions",
                params={"sort_by": sort_by, "order": order},
                headers=auth_headers
            )
            assert response.status_code == 200
