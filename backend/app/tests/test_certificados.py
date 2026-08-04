"""
Pruebas del módulo de certificados (Etapa 10): emisión, unicidad de
certificado vigente por joya, revocación con Optimistic Locking, y
generación server-side de número/hash.

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
        get_certificado_repository,
        get_certificado_service,
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
        get_certificado_repository,
        get_certificado_service,
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
        get_certificado_repository,
        get_certificado_service,
        get_registrador_version,
    ):
        fn.cache_clear()


AUTH = "/api/v1/auth"
CERT = "/api/v1/certificados"
JOY = "/api/v1/joyas"


def _token(client, correo="admin@terrae.co") -> str:
    resp = client.post(f"{AUTH}/login", json={"correo": correo, "password": "Terrae#2026"})
    return resp.json()["access_token"]


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _crear_joya(client, token) -> str:
    resp = client.post(
        JOY,
        json={"referencia": f"TR-CERT-{uuid.uuid4().hex[:8]}", "nombre": "Joya Certificable", "tipo": "anillo"},
        headers=_headers(token),
    )
    return resp.json()["id"]


def test_emitir_certificado_como_joyero(client):
    token = _token(client, correo="joyero@terrae.co")
    joya_id = _crear_joya(client, token)

    resp = client.post(CERT, json={"joya_id": joya_id}, headers=_headers(token))
    assert resp.status_code == 201
    body = resp.json()
    assert body["estado"] == "emitido"
    assert body["numero_certificado"].startswith("CERT-")
    assert len(body["hash_sha256"]) == 64
    assert body["version"] == 1


def test_emitir_certificado_como_cliente_devuelve_403(client):
    token = _token(client, correo="cliente@terrae.co")
    joya_id = _crear_joya(client, _token(client))
    resp = client.post(CERT, json={"joya_id": joya_id}, headers=_headers(token))
    assert resp.status_code == 403


def test_emitir_certificado_con_joya_inexistente_devuelve_404(client):
    token = _token(client)
    resp = client.post(CERT, json={"joya_id": "no-existe"}, headers=_headers(token))
    assert resp.status_code == 404


def test_emitir_segundo_certificado_vigente_para_misma_joya_devuelve_409(client):
    token = _token(client)
    joya_id = _crear_joya(client, token)

    r1 = client.post(CERT, json={"joya_id": joya_id}, headers=_headers(token))
    r2 = client.post(CERT, json={"joya_id": joya_id}, headers=_headers(token))
    assert r1.status_code == 201
    assert r2.status_code == 409


def test_dos_certificados_de_joyas_distintas_tienen_numero_y_hash_distintos(client):
    token = _token(client)
    joya_a = _crear_joya(client, token)
    joya_b = _crear_joya(client, token)

    cert_a = client.post(CERT, json={"joya_id": joya_a}, headers=_headers(token)).json()
    cert_b = client.post(CERT, json={"joya_id": joya_b}, headers=_headers(token)).json()

    assert cert_a["numero_certificado"] != cert_b["numero_certificado"]
    assert cert_a["hash_sha256"] != cert_b["hash_sha256"]


def test_revocar_certificado(client):
    token = _token(client)
    joya_id = _crear_joya(client, token)
    certificado = client.post(CERT, json={"joya_id": joya_id}, headers=_headers(token)).json()

    resp = client.post(
        f"{CERT}/{certificado['id']}/revocar",
        json={"version": 1, "motivo": "Error en los datos de la esmeralda"},
        headers=_headers(token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["estado"] == "revocado"
    assert body["version"] == 2


def test_revocar_certificado_ya_revocado_devuelve_422(client):
    token = _token(client)
    joya_id = _crear_joya(client, token)
    certificado = client.post(CERT, json={"joya_id": joya_id}, headers=_headers(token)).json()

    client.post(
        f"{CERT}/{certificado['id']}/revocar",
        json={"version": 1, "motivo": "Primera revocación"},
        headers=_headers(token),
    )
    resp = client.post(
        f"{CERT}/{certificado['id']}/revocar",
        json={"version": 2, "motivo": "Segunda revocación"},
        headers=_headers(token),
    )
    assert resp.status_code == 422


def test_revocar_con_version_desactualizada_devuelve_422(client):
    token = _token(client)
    joya_id = _crear_joya(client, token)
    certificado = client.post(CERT, json={"joya_id": joya_id}, headers=_headers(token)).json()

    resp = client.post(
        f"{CERT}/{certificado['id']}/revocar",
        json={"version": 99, "motivo": "Version incorrecta a propósito"},
        headers=_headers(token),
    )
    assert resp.status_code == 422


def test_emitir_nuevo_certificado_tras_revocar_el_anterior(client):
    token = _token(client)
    joya_id = _crear_joya(client, token)
    primero = client.post(CERT, json={"joya_id": joya_id}, headers=_headers(token)).json()

    client.post(
        f"{CERT}/{primero['id']}/revocar",
        json={"version": 1, "motivo": "Reemitir con datos correctos"},
        headers=_headers(token),
    )

    segundo = client.post(CERT, json={"joya_id": joya_id}, headers=_headers(token))
    assert segundo.status_code == 201
    assert segundo.json()["numero_certificado"] != primero["numero_certificado"]


def test_listar_certificados_con_filtro_por_estado(client):
    token = _token(client)
    joya_id = _crear_joya(client, token)
    certificado = client.post(CERT, json={"joya_id": joya_id}, headers=_headers(token)).json()

    resp = client.get(f"{CERT}?estado=emitido&joya_id={joya_id}", headers=_headers(token))
    body = resp.json()
    assert any(c["id"] == certificado["id"] for c in body["items"])
