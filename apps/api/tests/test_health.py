"""
Tests for API Health & Readiness Endpoints
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_returns_200():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "Shongoti API"
    assert "version" in data


def test_readiness_check_returns_database_status():
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"]["connected"] is True
    assert data["database"]["type"] in ["sqlite", "postgresql"]


def test_api_info_endpoint():
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert data["currency"] == "BDT"
    assert data["money_unit"] == "paisa"
