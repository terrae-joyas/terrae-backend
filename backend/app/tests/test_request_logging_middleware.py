"""
Pruebas de integración del RequestLoggingMiddleware (Etapa 7.5).

Verifica el comportamiento aditivo prometido: header `X-Request-ID` en
toda respuesta, sin alterar el contrato de los endpoints existentes
(mismo patrón de fixture aislada que test_auth.py).
"""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(monkeypatch):
    tmp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmp_dir, "usuarios_test.json")
    monkeypatch.setenv("USUARIOS_DATA_PATH", tmp_path)
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")

    from app.config import get_settings
    from app.dependencies import get_auth_service, get_jwt_handler, get_usuario_repository

    for fn in (get_settings, get_usuario_repository, get_jwt_handler, get_auth_service):
        fn.cache_clear()

    from app.main import app

    with TestClient(app) as c:
        yield c

    for fn in (get_settings, get_usuario_repository, get_jwt_handler, get_auth_service):
        fn.cache_clear()


def test_toda_respuesta_incluye_header_request_id(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert "X-Request-ID" in resp.headers
    # Es un UUID válido (36 caracteres con guiones)
    assert len(resp.headers["X-Request-ID"]) == 36


def test_request_id_es_distinto_en_cada_request(client):
    resp1 = client.get("/health")
    resp2 = client.get("/health")
    assert resp1.headers["X-Request-ID"] != resp2.headers["X-Request-ID"]


def test_middleware_no_altera_el_cuerpo_de_la_respuesta_existente(client):
    """Garantiza que agregar el middleware en la Etapa 7.5 no cambió el
    contrato ya probado del endpoint /health desde la Etapa 2."""
    resp = client.get("/health")
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "terrae-backend"


def test_middleware_no_rompe_flujo_de_login_existente(client):
    """Confirma que el endpoint de login (Etapa 4) sigue funcionando
    exactamente igual con el middleware activo."""
    resp = client.post(
        "/api/v1/auth/login", json={"correo": "admin@terrae.co", "password": "Terrae#2026"}
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    assert "X-Request-ID" in resp.headers


def test_middleware_no_rompe_respuestas_de_error_existentes(client):
    """El manejo de errores de la Etapa 4 (401 en login inválido) sigue
    intacto con el middleware activo."""
    resp = client.post(
        "/api/v1/auth/login", json={"correo": "admin@terrae.co", "password": "incorrecta"}
    )
    assert resp.status_code == 401
    assert "X-Request-ID" in resp.headers
