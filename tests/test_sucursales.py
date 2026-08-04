"""
Pruebas del módulo de sucursales (Etapa 6): CRUD, paginación, filtrado
y control de acceso por rol. Reutiliza el mismo patrón de fixture
aislada de `test_auth.py`.
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
    from app.dependencies import (
        get_auth_service,
        get_jwt_handler,
        get_sucursal_repository,
        get_sucursal_service,
        get_usuario_repository,
    )

    get_settings.cache_clear()
    get_usuario_repository.cache_clear()
    get_jwt_handler.cache_clear()
    get_auth_service.cache_clear()
    get_sucursal_repository.cache_clear()
    get_sucursal_service.cache_clear()

    from app.main import app

    with TestClient(app) as c:
        yield c

    get_settings.cache_clear()
    get_usuario_repository.cache_clear()
    get_jwt_handler.cache_clear()
    get_auth_service.cache_clear()
    get_sucursal_repository.cache_clear()
    get_sucursal_service.cache_clear()


AUTH = "/api/v1/auth"
SUC = "/api/v1/sucursales"


def _token_admin(client) -> str:
    resp = client.post(f"{AUTH}/login", json={"correo": "admin@terrae.co", "password": "Terrae#2026"})
    return resp.json()["access_token"]


def _token_cliente(client) -> str:
    resp = client.post(
        f"{AUTH}/login", json={"correo": "cliente@terrae.co", "password": "Terrae#2026"}
    )
    return resp.json()["access_token"]


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _crear_sucursal(client, token, **overrides):
    payload = {
        "nombre": "Taller Bogotá",
        "tipo": "taller",
        "ciudad": "Bogotá",
        "direccion": "Calle 100",
    }
    payload.update(overrides)
    return client.post(SUC, json=payload, headers=_headers(token))


def test_listar_sin_autenticacion_devuelve_401_o_403(client):
    resp = client.get(SUC)
    assert resp.status_code in (401, 403)


def test_crear_sucursal_como_administrador(client):
    token = _token_admin(client)
    resp = _crear_sucursal(client, token)
    assert resp.status_code == 201
    body = resp.json()
    assert body["nombre"] == "Taller Bogotá"
    assert body["tipo"] == "taller"
    assert body["activa"] is True


def test_crear_sucursal_como_cliente_devuelve_403(client):
    token = _token_cliente(client)
    resp = _crear_sucursal(client, token)
    assert resp.status_code == 403


def test_crear_sucursal_con_tipo_invalido_devuelve_422(client):
    token = _token_admin(client)
    resp = _crear_sucursal(client, token, tipo="tipo_inexistente")
    assert resp.status_code == 422


def test_obtener_sucursal_por_id(client):
    token = _token_admin(client)
    creada = _crear_sucursal(client, token).json()

    resp = client.get(f"{SUC}/{creada['id']}", headers=_headers(token))
    assert resp.status_code == 200
    assert resp.json()["id"] == creada["id"]


def test_obtener_sucursal_inexistente_devuelve_404(client):
    token = _token_admin(client)
    resp = client.get(f"{SUC}/no-existe", headers=_headers(token))
    assert resp.status_code == 404


def test_actualizar_sucursal(client):
    token = _token_admin(client)
    creada = _crear_sucursal(client, token).json()

    resp = client.put(
        f"{SUC}/{creada['id']}",
        json={
            "nombre": "Taller Bogotá Renovado",
            "tipo": "taller",
            "ciudad": "Bogotá",
            "direccion": "Nueva dirección",
            "activa": True,
        },
        headers=_headers(token),
    )
    assert resp.status_code == 200
    assert resp.json()["nombre"] == "Taller Bogotá Renovado"


def test_desactivar_sucursal_es_baja_logica(client):
    token = _token_admin(client)
    creada = _crear_sucursal(client, token).json()

    resp = client.delete(f"{SUC}/{creada['id']}", headers=_headers(token))
    assert resp.status_code == 200
    assert resp.json()["activa"] is False

    # Sigue existiendo (no fue un DELETE físico)
    resp_get = client.get(f"{SUC}/{creada['id']}", headers=_headers(token))
    assert resp_get.status_code == 200


def test_listar_con_paginacion(client):
    token = _token_admin(client)
    for i in range(5):
        _crear_sucursal(client, token, nombre=f"Sucursal {i}", ciudad="Medellín")

    resp = client.get(f"{SUC}?pagina=1&tamano_pagina=2", headers=_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) == 2
    assert body["total"] == 5
    assert body["total_paginas"] == 3
    assert body["pagina"] == 1


def test_listar_con_filtro_por_ciudad(client):
    token = _token_admin(client)
    _crear_sucursal(client, token, nombre="Bogotá 1", ciudad="Bogotá")
    _crear_sucursal(client, token, nombre="Cali 1", ciudad="Cali")

    resp = client.get(f"{SUC}?ciudad=cali", headers=_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["ciudad"] == "Cali"


def test_listar_con_filtro_por_tipo(client):
    token = _token_admin(client)
    _crear_sucursal(client, token, nombre="Taller X", tipo="taller")
    _crear_sucursal(client, token, nombre="Tienda X", tipo="punto_venta")

    resp = client.get(f"{SUC}?tipo=punto_venta", headers=_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["tipo"] == "punto_venta"
