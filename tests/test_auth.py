"""
Pruebas del módulo de autenticación (Etapa 4).

Usa un archivo JSON temporal por sesión de pruebas (vía monkeypatch de
settings) para no interferir con los datos de desarrollo reales ni con
la semilla demo.
"""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(monkeypatch):
    """Crea un cliente de pruebas con un repositorio de usuarios en un
    archivo JSON temporal y aislado por test."""
    tmp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmp_dir, "usuarios_test.json")
    monkeypatch.setenv("USUARIOS_DATA_PATH", tmp_path)
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")

    # Importar después de fijar las env vars para que Settings las lea,
    # y limpiar cachés de lru_cache entre tests.
    from app.config import get_settings
    from app.dependencies import get_auth_service, get_jwt_handler, get_usuario_repository

    get_settings.cache_clear()
    get_usuario_repository.cache_clear()
    get_jwt_handler.cache_clear()
    get_auth_service.cache_clear()

    from app.main import app

    with TestClient(app) as c:
        yield c

    get_settings.cache_clear()
    get_usuario_repository.cache_clear()
    get_jwt_handler.cache_clear()
    get_auth_service.cache_clear()


BASE = "/api/v1/auth"


def _registrar_y_login(client, correo="nueva@terrae.co", password="Password123"):
    client.post(
        f"{BASE}/registro",
        json={
            "nombre_completo": "Usuario de Prueba",
            "correo": correo,
            "password": password,
            "confirmar_password": password,
        },
    )
    resp = client.post(f"{BASE}/login", json={"correo": correo, "password": password})
    return resp


def test_registro_exitoso_crea_usuario_con_rol_cliente(client):
    resp = client.post(
        f"{BASE}/registro",
        json={
            "nombre_completo": "María Cliente",
            "correo": "maria@terrae.co",
            "password": "Password123",
            "confirmar_password": "Password123",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["correo"] == "maria@terrae.co"
    assert body["rol"] == "cliente"
    assert body["activo"] is True
    assert "hashed_password" not in body  # nunca se expone el hash


def test_registro_con_correo_duplicado_devuelve_409(client):
    payload = {
        "nombre_completo": "Duplicado",
        "correo": "dup@terrae.co",
        "password": "Password123",
        "confirmar_password": "Password123",
    }
    r1 = client.post(f"{BASE}/registro", json=payload)
    r2 = client.post(f"{BASE}/registro", json=payload)
    assert r1.status_code == 201
    assert r2.status_code == 409


def test_registro_con_passwords_no_coincidentes_devuelve_422(client):
    resp = client.post(
        f"{BASE}/registro",
        json={
            "nombre_completo": "Error Password",
            "correo": "error@terrae.co",
            "password": "Password123",
            "confirmar_password": "OtraPassword456",
        },
    )
    assert resp.status_code == 422


def test_login_exitoso_devuelve_tokens(client):
    resp = _registrar_y_login(client)
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"
    assert body["expires_in"] > 0


def test_login_con_password_incorrecta_devuelve_401(client):
    client.post(
        f"{BASE}/registro",
        json={
            "nombre_completo": "Test 401",
            "correo": "test401@terrae.co",
            "password": "Password123",
            "confirmar_password": "Password123",
        },
    )
    resp = client.post(
        f"{BASE}/login", json={"correo": "test401@terrae.co", "password": "Incorrecta"}
    )
    assert resp.status_code == 401


def test_endpoint_protegido_sin_token_devuelve_403_o_401(client):
    resp = client.get(f"{BASE}/yo")
    assert resp.status_code in (401, 403)


def test_endpoint_yo_con_token_valido_devuelve_datos_del_usuario(client):
    login_resp = _registrar_y_login(client, correo="yo@terrae.co")
    token = login_resp.json()["access_token"]

    resp = client.get(f"{BASE}/yo", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["correo"] == "yo@terrae.co"


def test_refrescar_token_emite_nuevo_access_token(client):
    login_resp = _registrar_y_login(client, correo="refresh@terrae.co")
    refresh_token = login_resp.json()["refresh_token"]

    resp = client.post(f"{BASE}/refrescar", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_refrescar_con_access_token_en_vez_de_refresh_falla(client):
    login_resp = _registrar_y_login(client, correo="mixto@terrae.co")
    access_token = login_resp.json()["access_token"]

    # Usar un access_token donde se espera un refresh_token debe fallar
    resp = client.post(f"{BASE}/refrescar", json={"refresh_token": access_token})
    assert resp.status_code == 401


def test_endpoint_solo_administradores_rechaza_rol_cliente(client):
    login_resp = _registrar_y_login(client, correo="cliente-normal@terrae.co")
    token = login_resp.json()["access_token"]

    resp = client.get(
        f"{BASE}/solo-administradores", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 403


def test_usuarios_demo_sembrados_permiten_login_admin(client):
    """Verifica que la semilla demo (admin@terrae.co) se creó y permite
    login, y que sí tiene acceso al endpoint solo-administradores."""
    resp = client.post(
        f"{BASE}/login", json={"correo": "admin@terrae.co", "password": "Terrae#2026"}
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    resp_admin = client.get(
        f"{BASE}/solo-administradores", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp_admin.status_code == 200
