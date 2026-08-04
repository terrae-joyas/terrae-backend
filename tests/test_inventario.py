"""
Pruebas del módulo de inventario (Etapa 9): creación, validaciones
cruzadas (joya/sucursal deben existir), ajuste de cantidad por delta
(ADR-009-01), movimiento con Optimistic Locking, y regresión de que
completar InventarioModel (ADR-009-02) no rompió nada de Joyas.

Requiere PostgreSQL real (mismo patrón que las suites anteriores).
"""

import os
import tempfile
import uuid

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
        get_esmeralda_repository,
        get_esmeralda_service,
        get_inventario_repository,
        get_inventario_service,
        get_joya_repository,
        get_joya_service,
        get_jwt_handler,
        get_registrador_version,
        get_sucursal_repository,
        get_sucursal_service,
        get_usuario_repository,
    )
    from app.infrastructure.db.session import get_engine, get_session_factory

    # get_event_bus() NO se limpia — conserva el consumidor de logging
    # de auditoría suscrito en la importación de app.main (ver
    # test_esmeraldas.py, mismo razonamiento de la Etapa 8).
    for fn in (
        get_settings,
        get_usuario_repository,
        get_jwt_handler,
        get_auth_service,
        get_sucursal_repository,
        get_sucursal_service,
        get_joya_repository,
        get_joya_service,
        get_esmeralda_repository,
        get_esmeralda_service,
        get_inventario_repository,
        get_inventario_service,
        get_registrador_version,
        get_engine,
        get_session_factory,
    ):
        fn.cache_clear()

    from app.main import app

    with TestClient(app) as c:
        yield c

    for fn in (
        get_settings,
        get_usuario_repository,
        get_jwt_handler,
        get_auth_service,
        get_sucursal_repository,
        get_sucursal_service,
        get_joya_repository,
        get_joya_service,
        get_esmeralda_repository,
        get_esmeralda_service,
        get_inventario_repository,
        get_inventario_service,
        get_registrador_version,
    ):
        fn.cache_clear()


AUTH = "/api/v1/auth"
INV = "/api/v1/inventario"
JOY = "/api/v1/joyas"
SUC = "/api/v1/sucursales"


def _token(client, correo="admin@terrae.co") -> str:
    resp = client.post(f"{AUTH}/login", json={"correo": correo, "password": "Terrae#2026"})
    return resp.json()["access_token"]


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _crear_sucursal(client, token) -> str:
    resp = client.post(
        SUC,
        json={"nombre": f"Sucursal {uuid.uuid4().hex[:6]}", "tipo": "taller", "ciudad": "Bogotá"},
        headers=_headers(token),
    )
    return resp.json()["id"]


def _crear_joya(client, token) -> str:
    resp = client.post(
        JOY,
        json={
            "referencia": f"TR-INV-{uuid.uuid4().hex[:8]}",
            "nombre": "Joya de Prueba Inventario",
            "tipo": "anillo",
        },
        headers=_headers(token),
    )
    return resp.json()["id"]


def _crear_inventario(client, token, joya_id=None, sucursal_id=None, **overrides):
    payload = {
        "joya_id": joya_id or _crear_joya(client, token),
        "sucursal_id": sucursal_id or _crear_sucursal(client, token),
        "cantidad": 5,
    }
    payload.update(overrides)
    return client.post(INV, json=payload, headers=_headers(token))


# --- Creación y validaciones cruzadas ---


def test_crear_inventario_como_joyero(client):
    token = _token(client, correo="joyero@terrae.co")
    resp = _crear_inventario(client, token)
    assert resp.status_code == 201
    body = resp.json()
    assert body["cantidad"] == 5
    assert body["version"] == 1
    assert body["creado_por"] is not None


def test_crear_inventario_como_cliente_devuelve_403(client):
    token = _token(client, correo="cliente@terrae.co")
    resp = _crear_inventario(client, token)
    assert resp.status_code == 403


def test_crear_inventario_con_joya_inexistente_devuelve_404(client):
    token = _token(client)
    sucursal_id = _crear_sucursal(client, token)
    resp = _crear_inventario(client, token, joya_id="no-existe", sucursal_id=sucursal_id)
    assert resp.status_code == 404


def test_crear_inventario_con_sucursal_inexistente_devuelve_404(client):
    token = _token(client)
    joya_id = _crear_joya(client, token)
    resp = _crear_inventario(client, token, joya_id=joya_id, sucursal_id="no-existe")
    assert resp.status_code == 404


def test_crear_segundo_inventario_para_misma_joya_devuelve_409(client):
    token = _token(client)
    joya_id = _crear_joya(client, token)
    sucursal_id = _crear_sucursal(client, token)

    r1 = _crear_inventario(client, token, joya_id=joya_id, sucursal_id=sucursal_id)
    r2 = _crear_inventario(client, token, joya_id=joya_id, sucursal_id=sucursal_id)
    assert r1.status_code == 201
    assert r2.status_code == 409


def test_obtener_inventario_por_joya(client):
    token = _token(client)
    joya_id = _crear_joya(client, token)
    sucursal_id = _crear_sucursal(client, token)
    _crear_inventario(client, token, joya_id=joya_id, sucursal_id=sucursal_id)

    resp = client.get(f"{INV}/joya/{joya_id}", headers=_headers(token))
    assert resp.status_code == 200
    assert resp.json()["joya_id"] == joya_id


def test_obtener_inventario_de_joya_sin_registro_devuelve_404(client):
    token = _token(client)
    joya_id = _crear_joya(client, token)
    resp = client.get(f"{INV}/joya/{joya_id}", headers=_headers(token))
    assert resp.status_code == 404


# --- Ajuste de cantidad por delta (ADR-009-01) ---


def test_ajustar_cantidad_positivo(client):
    token = _token(client)
    creado = _crear_inventario(client, token, cantidad=5).json()

    resp = client.patch(
        f"{INV}/{creado['id']}/ajustar",
        json={"delta": 3, "motivo": "Reposición de taller", "version": 1},
        headers=_headers(token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["cantidad"] == 8
    assert body["version"] == 2


def test_ajustar_cantidad_negativo(client):
    token = _token(client)
    creado = _crear_inventario(client, token, cantidad=5).json()

    resp = client.patch(
        f"{INV}/{creado['id']}/ajustar",
        json={"delta": -2, "motivo": "Venta en mostrador", "version": 1},
        headers=_headers(token),
    )
    assert resp.status_code == 200
    assert resp.json()["cantidad"] == 3


def test_ajustar_cantidad_que_resultaria_negativa_devuelve_422(client):
    token = _token(client)
    creado = _crear_inventario(client, token, cantidad=2).json()

    resp = client.patch(
        f"{INV}/{creado['id']}/ajustar",
        json={"delta": -5, "motivo": "Intento de sobreventa", "version": 1},
        headers=_headers(token),
    )
    assert resp.status_code == 422


def test_ajustar_cantidad_sin_motivo_devuelve_422_validacion(client):
    token = _token(client)
    creado = _crear_inventario(client, token, cantidad=5).json()

    resp = client.patch(
        f"{INV}/{creado['id']}/ajustar",
        json={"delta": 1, "motivo": "", "version": 1},
        headers=_headers(token),
    )
    assert resp.status_code == 422


def test_ajustar_cantidad_con_version_desactualizada_devuelve_422(client):
    token = _token(client)
    creado = _crear_inventario(client, token, cantidad=5).json()

    client.patch(
        f"{INV}/{creado['id']}/ajustar",
        json={"delta": 1, "motivo": "Primer ajuste", "version": 1},
        headers=_headers(token),
    )
    # Reutiliza la versión vieja (1) — debe fallar por conflicto
    resp = client.patch(
        f"{INV}/{creado['id']}/ajustar",
        json={"delta": 1, "motivo": "Segundo ajuste con version vieja", "version": 1},
        headers=_headers(token),
    )
    assert resp.status_code == 422


def test_ajustes_secuenciales_incrementan_version_y_cantidad_correctamente(client):
    token = _token(client)
    creado = _crear_inventario(client, token, cantidad=10).json()

    r1 = client.patch(
        f"{INV}/{creado['id']}/ajustar",
        json={"delta": -3, "motivo": "Venta 1", "version": 1},
        headers=_headers(token),
    )
    assert r1.json()["cantidad"] == 7
    assert r1.json()["version"] == 2

    r2 = client.patch(
        f"{INV}/{creado['id']}/ajustar",
        json={"delta": -2, "motivo": "Venta 2", "version": 2},
        headers=_headers(token),
    )
    assert r2.json()["cantidad"] == 5
    assert r2.json()["version"] == 3


# --- Mover (sucursal/ubicación) ---


def test_mover_inventario_a_otra_sucursal(client):
    token = _token(client)
    sucursal_origen = _crear_sucursal(client, token)
    sucursal_destino = _crear_sucursal(client, token)
    creado = _crear_inventario(client, token, sucursal_id=sucursal_origen).json()

    resp = client.put(
        f"{INV}/{creado['id']}/mover",
        json={"sucursal_id": sucursal_destino, "ubicacion_fisica": "Vitrina 2", "version": 1},
        headers=_headers(token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["sucursal_id"] == sucursal_destino
    assert body["ubicacion_fisica"] == "Vitrina 2"
    assert body["cantidad"] == 5  # mover NO toca cantidad


def test_mover_a_sucursal_inexistente_devuelve_404(client):
    token = _token(client)
    creado = _crear_inventario(client, token).json()

    resp = client.put(
        f"{INV}/{creado['id']}/mover",
        json={"sucursal_id": "no-existe", "version": 1},
        headers=_headers(token),
    )
    assert resp.status_code == 404


# --- Filtros y paginación ---


def test_listar_con_filtro_por_sucursal(client):
    token = _token(client)
    sucursal_a = _crear_sucursal(client, token)
    sucursal_b = _crear_sucursal(client, token)
    _crear_inventario(client, token, sucursal_id=sucursal_a)
    _crear_inventario(client, token, sucursal_id=sucursal_b)

    resp = client.get(f"{INV}?sucursal_id={sucursal_a}", headers=_headers(token))
    body = resp.json()
    assert all(i["sucursal_id"] == sucursal_a for i in body["items"])
    assert body["total"] >= 1
