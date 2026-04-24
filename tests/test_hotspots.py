import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_get_hotspots_map(auth_headers):
    response = client.get("/api/v1/analytics/reports/hotspots-map", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "points" in data
    assert isinstance(data["points"], list)
