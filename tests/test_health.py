"""Pruebas de humo (smoke tests) de la Etapa 2 — validan que el entorno
del backend está correctamente configurado."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "terrae-backend"


def test_root_returns_welcome_message():
    response = client.get("/")
    assert response.status_code == 200
    assert "docs" in response.json()
