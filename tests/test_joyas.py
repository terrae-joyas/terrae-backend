"""
Pruebas del módulo de joyas (Etapa 7): CRUD, validaciones de negocio
(esmeralda/sucursal asociadas) y máquina de estados.

Requiere PostgreSQL real (igual que test_sucursales.py) porque
`PostgresJoyaRepository` y `PostgresEsmeraldaRepository` no tienen
fallback ni fueron diseñados contra SQLite en esta suite.
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
        get_joya_repository,
        get_joya_service,
        get_jwt_handler,
        get_sucursal_repository,
        get_sucursal_service,
        get_usuario_repository,
    )

    for fn in (
        get_settings,
        get_usuario_repository,
        get_jwt_handler,
        get_auth_service,
        get_sucursal_repository,
        get_sucursal_service,
        get_esmeralda_repository,
        get_joya_repository,
        get_joya_service,
    ):
        fn.cache_clear()

    from app.infrastructure.db.session import get_engine, get_session_factory

    get_engine.cache_clear()
    get_session_factory.cache_clear()

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
        get_esmeralda_repository,
        get_joya_repository,
        get_joya_service,
    ):
        fn.cache_clear()


AUTH = "/api/v1/auth"
JOY = "/api/v1/joyas"


def _token(client, correo="admin@terrae.co") -> str:
    resp = client.post(f"{AUTH}/login", json={"correo": correo, "password": "Terrae#2026"})
    return resp.json()["access_token"]


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _crear_esmeralda_directo() -> str:
    """Inserta una esmeralda directamente vía el ORM (no hay endpoint
    todavía: el CRUD de esmeraldas es objeto de la Etapa 8)."""
    from app.infrastructure.db.session import get_session_factory
    from app.infrastructure.db.models.gemologia import EsmeraldaModel

    session_factory = get_session_factory()
    esmeralda_id = str(uuid.uuid4())
    with session_factory() as session:
        session.add(
            EsmeraldaModel(
                id=esmeralda_id,
                codigo_interno=f"ESM-TEST-{esmeralda_id[:8]}",
                mina_origen="Muzo",
                quilates=1.5,
            )
        )
        session.commit()
    return esmeralda_id


def _crear_joya(client, token, **overrides):
    payload = {
        "referencia": f"TR-TEST-{uuid.uuid4().hex[:8]}",
        "nombre": "Anillo de Prueba",
        "tipo": "anillo",
    }
    payload.update(overrides)
    return client.post(JOY, json=payload, headers=_headers(token))


def test_crear_joya_como_joyero(client):
    token = _token(client, correo="joyero@terrae.co")
    resp = _crear_joya(client, token)
    assert resp.status_code == 201
    assert resp.json()["estado"] == "en_taller"


def test_crear_joya_como_cliente_devuelve_403(client):
    token = _token(client, correo="cliente@terrae.co")
    resp = _crear_joya(client, token)
    assert resp.status_code == 403


def test_crear_joya_con_referencia_duplicada_devuelve_409(client):
    token = _token(client)
    ref = f"TR-DUP-{uuid.uuid4().hex[:8]}"
    r1 = _crear_joya(client, token, referencia=ref)
    r2 = _crear_joya(client, token, referencia=ref)
    assert r1.status_code == 201
    assert r2.status_code == 409


def test_crear_joya_con_esmeralda_inexistente_devuelve_404(client):
    token = _token(client)
    resp = _crear_joya(client, token, esmeralda_id="no-existe")
    assert resp.status_code == 404


def test_crear_joya_con_esmeralda_valida(client):
    token = _token(client)
    esmeralda_id = _crear_esmeralda_directo()
    resp = _crear_joya(client, token, esmeralda_id=esmeralda_id)
    assert resp.status_code == 201
    assert resp.json()["esmeralda_id"] == esmeralda_id


def test_no_se_puede_vincular_esmeralda_a_dos_joyas_activas(client):
    token = _token(client)
    esmeralda_id = _crear_esmeralda_directo()

    r1 = _crear_joya(client, token, esmeralda_id=esmeralda_id)
    assert r1.status_code == 201

    r2 = _crear_joya(client, token, esmeralda_id=esmeralda_id)
    assert r2.status_code == 409


def test_crear_joya_con_sucursal_inexistente_devuelve_404(client):
    token = _token(client)
    resp = _crear_joya(client, token, sucursal_id="no-existe")
    assert resp.status_code == 404


def test_obtener_joya_inexistente_devuelve_404(client):
    token = _token(client)
    resp = client.get(f"{JOY}/no-existe", headers=_headers(token))
    assert resp.status_code == 404


def test_actualizar_joya(client):
    token = _token(client)
    creada = _crear_joya(client, token).json()

    resp = client.put(
        f"{JOY}/{creada['id']}",
        json={"nombre": "Anillo Renombrado", "tipo": "anillo"},
        headers=_headers(token),
    )
    assert resp.status_code == 200
    assert resp.json()["nombre"] == "Anillo Renombrado"


def test_cambiar_estado_transicion_valida(client):
    token = _token(client)
    creada = _crear_joya(client, token).json()
    assert creada["estado"] == "en_taller"

    resp = client.patch(
        f"{JOY}/{creada['id']}/estado",
        json={"nuevo_estado": "disponible"},
        headers=_headers(token),
    )
    assert resp.status_code == 200
    assert resp.json()["estado"] == "disponible"


def test_cambiar_estado_transicion_invalida_devuelve_422(client):
    token = _token(client)
    creada = _crear_joya(client, token).json()  # en_taller

    # en_taller -> en_reparacion no es una transición válida
    resp = client.patch(
        f"{JOY}/{creada['id']}/estado",
        json={"nuevo_estado": "en_reparacion"},
        headers=_headers(token),
    )
    assert resp.status_code == 422


def test_no_se_puede_marcar_vendida_directamente(client):
    token = _token(client)
    creada = _crear_joya(client, token).json()

    resp = client.patch(
        f"{JOY}/{creada['id']}/estado",
        json={"nuevo_estado": "vendida"},
        headers=_headers(token),
    )
    assert resp.status_code == 422
    assert "venta" in resp.json()["detail"].lower()


def test_listar_joyas_con_filtro_por_estado(client):
    token = _token(client)
    j1 = _crear_joya(client, token).json()
    _crear_joya(client, token)  # otra en_taller también

    client.patch(f"{JOY}/{j1['id']}/estado", json={"nuevo_estado": "disponible"}, headers=_headers(token))

    resp = client.get(f"{JOY}?estado=disponible", headers=_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == j1["id"]
