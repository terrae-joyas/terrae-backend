"""
Pruebas del módulo de activos multimedia (Etapa 10): validación de
formato de hash SHA-256, validación de existencia de la entidad
relacionada (Joya/Esmeralda/Certificado), y baja lógica.

Requiere PostgreSQL real (mismo patrón que las suites anteriores).
"""

import os
import tempfile
import uuid

import pytest
from fastapi.testclient import TestClient

HASH_VALIDO = "a" * 64


@pytest.fixture()
def client(monkeypatch):
    tmp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmp_dir, "usuarios_test.json")
    monkeypatch.setenv("USUARIOS_DATA_PATH", tmp_path)
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")

    from app.config import get_settings
    from app.dependencies import (
        get_activo_multimedia_repository,
        get_activo_multimedia_service,
        get_auth_service,
        get_joya_repository,
        get_joya_service,
        get_jwt_handler,
        get_registrador_version,
        get_sucursal_repository,
        get_sucursal_service,
        get_usuario_repository,
    )
    from app.infrastructure.db.session import get_engine, get_session_factory

    for fn in (
        get_settings,
        get_usuario_repository,
        get_jwt_handler,
        get_auth_service,
        get_sucursal_repository,
        get_sucursal_service,
        get_joya_repository,
        get_joya_service,
        get_activo_multimedia_repository,
        get_activo_multimedia_service,
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
        get_activo_multimedia_repository,
        get_activo_multimedia_service,
        get_registrador_version,
    ):
        fn.cache_clear()


AUTH = "/api/v1/auth"
ACT = "/api/v1/activos-multimedia"
JOY = "/api/v1/joyas"


def _token(client, correo="admin@terrae.co") -> str:
    resp = client.post(f"{AUTH}/login", json={"correo": correo, "password": "Terrae#2026"})
    return resp.json()["access_token"]


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _crear_joya(client, token) -> str:
    resp = client.post(
        JOY,
        json={"referencia": f"TR-MM-{uuid.uuid4().hex[:8]}", "nombre": "Joya con Fotos", "tipo": "anillo"},
        headers=_headers(token),
    )
    return resp.json()["id"]


def test_crear_activo_multimedia_para_joya_valida(client):
    token = _token(client, correo="joyero@terrae.co")
    joya_id = _crear_joya(client, token)

    resp = client.post(
        ACT,
        json={
            "entidad_tipo": "Joya",
            "entidad_id": joya_id,
            "tipo": "foto_joya",
            "url": "https://cdn.terrae.co/joyas/foto1.jpg",
            "hash_sha256": HASH_VALIDO,
            "dispositivo": "Canon EOS R5",
        },
        headers=_headers(token),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["entidad_tipo"] == "Joya"
    assert body["dispositivo"] == "Canon EOS R5"
    assert body["creado_por"] is not None  # autor
    assert body["creado_en"] is not None  # fecha
    assert body["version"] == 1  # versión


def test_crear_activo_multimedia_como_cliente_devuelve_403(client):
    token = _token(client, correo="cliente@terrae.co")
    joya_id = _crear_joya(client, _token(client))
    resp = client.post(
        ACT,
        json={
            "entidad_tipo": "Joya",
            "entidad_id": joya_id,
            "tipo": "foto_joya",
            "url": "https://cdn.terrae.co/joyas/foto1.jpg",
            "hash_sha256": HASH_VALIDO,
        },
        headers=_headers(token),
    )
    assert resp.status_code == 403


def test_crear_activo_con_hash_invalido_devuelve_422(client):
    token = _token(client)
    joya_id = _crear_joya(client, token)
    resp = client.post(
        ACT,
        json={
            "entidad_tipo": "Joya",
            "entidad_id": joya_id,
            "tipo": "foto_joya",
            "url": "https://cdn.terrae.co/joyas/foto1.jpg",
            "hash_sha256": "hash-invalido-demasiado-corto",
        },
        headers=_headers(token),
    )
    assert resp.status_code == 422


def test_crear_activo_para_joya_inexistente_devuelve_404(client):
    token = _token(client)
    resp = client.post(
        ACT,
        json={
            "entidad_tipo": "Joya",
            "entidad_id": "no-existe",
            "tipo": "foto_joya",
            "url": "https://cdn.terrae.co/joyas/foto1.jpg",
            "hash_sha256": HASH_VALIDO,
        },
        headers=_headers(token),
    )
    assert resp.status_code == 404


def test_crear_activo_con_entidad_tipo_desconocido_no_valida_existencia(client):
    """Tipos de entidad sin validador registrado (ver
    ActivoMultimediaService.registrar_validador) se aceptan sin
    validar existencia — extensibilidad documentada en ADR-010-01."""
    token = _token(client)
    resp = client.post(
        ACT,
        json={
            "entidad_tipo": "TipoFuturoSinValidador",
            "entidad_id": "cualquier-id",
            "tipo": "recurso_visual",
            "url": "https://cdn.terrae.co/recursos/x.jpg",
            "hash_sha256": HASH_VALIDO,
        },
        headers=_headers(token),
    )
    assert resp.status_code == 201


def test_desactivar_activo_multimedia_es_baja_logica(client):
    token = _token(client)
    joya_id = _crear_joya(client, token)
    creado = client.post(
        ACT,
        json={
            "entidad_tipo": "Joya",
            "entidad_id": joya_id,
            "tipo": "foto_joya",
            "url": "https://cdn.terrae.co/joyas/foto1.jpg",
            "hash_sha256": HASH_VALIDO,
        },
        headers=_headers(token),
    ).json()

    resp = client.delete(f"{ACT}/{creado['id']}", headers=_headers(token))
    assert resp.status_code == 200

    resp_listado = client.get(f"{ACT}?entidad_tipo=Joya&entidad_id={joya_id}", headers=_headers(token))
    ids = [a["id"] for a in resp_listado.json()["items"]]
    assert creado["id"] not in ids


def test_listar_activos_filtrados_por_entidad(client):
    token = _token(client)
    joya_id = _crear_joya(client, token)
    client.post(
        ACT,
        json={
            "entidad_tipo": "Joya",
            "entidad_id": joya_id,
            "tipo": "foto_joya",
            "url": "https://cdn.terrae.co/joyas/foto1.jpg",
            "hash_sha256": HASH_VALIDO,
        },
        headers=_headers(token),
    )

    resp = client.get(f"{ACT}?entidad_tipo=Joya&entidad_id={joya_id}", headers=_headers(token))
    body = resp.json()
    assert body["total"] >= 1
    assert all(a["entidad_id"] == joya_id for a in body["items"])
