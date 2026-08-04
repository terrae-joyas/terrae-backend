"""
Pruebas del módulo de esmeraldas (Etapa 8): CRUD, auditoría,
versionado, Optimistic Locking, Domain Events y regresión de Joyas
(ADR-008-02: confirmar que completar Esmeralda no rompió JoyaService).

Requiere PostgreSQL real (mismo patrón que test_sucursales.py y
test_joyas.py).
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
        get_joya_repository,
        get_joya_service,
        get_jwt_handler,
        get_registrador_version,
        get_sucursal_repository,
        get_sucursal_service,
        get_usuario_repository,
    )
    from app.infrastructure.db.session import get_engine, get_session_factory

    # Nota: get_event_bus() NO se limpia a propósito — conserva el
    # consumidor de logging de auditoría suscrito en la importación de
    # app.main (ADR-008-03); limpiarlo perdería la suscripción, ya que
    # `configurar_event_bus()` solo se ejecuta una vez al importar el
    # módulo, no en cada test.
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
        get_registrador_version,
    ):
        fn.cache_clear()


AUTH = "/api/v1/auth"
ESM = "/api/v1/esmeraldas"
JOY = "/api/v1/joyas"


def _token(client, correo="admin@terrae.co") -> str:
    resp = client.post(f"{AUTH}/login", json={"correo": correo, "password": "Terrae#2026"})
    return resp.json()["access_token"]


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _crear_esmeralda(client, token, **overrides):
    payload = {
        "codigo_interno": f"ESM-TEST-{uuid.uuid4().hex[:8]}",
        "mina_origen": "Muzo",
        "quilates": 2.1,
    }
    payload.update(overrides)
    return client.post(ESM, json=payload, headers=_headers(token))


# --- CRUD básico ---


def test_crear_esmeralda_como_joyero(client):
    token = _token(client, correo="joyero@terrae.co")
    resp = _crear_esmeralda(client, token)
    assert resp.status_code == 201
    body = resp.json()
    assert body["mina_origen"] == "Muzo"
    assert body["version"] == 1


def test_crear_esmeralda_como_cliente_devuelve_403(client):
    token = _token(client, correo="cliente@terrae.co")
    resp = _crear_esmeralda(client, token)
    assert resp.status_code == 403


def test_crear_esmeralda_con_codigo_duplicado_devuelve_409(client):
    token = _token(client)
    codigo = f"ESM-DUP-{uuid.uuid4().hex[:8]}"
    r1 = _crear_esmeralda(client, token, codigo_interno=codigo)
    r2 = _crear_esmeralda(client, token, codigo_interno=codigo)
    assert r1.status_code == 201
    assert r2.status_code == 409


def test_crear_esmeralda_con_quilates_invalidos_devuelve_422(client):
    token = _token(client)
    resp = _crear_esmeralda(client, token, quilates=-1)
    assert resp.status_code == 422


def test_obtener_esmeralda_inexistente_devuelve_404(client):
    token = _token(client)
    resp = client.get(f"{ESM}/no-existe", headers=_headers(token))
    assert resp.status_code == 404


# --- Auditoría ---


def test_esmeralda_creada_registra_auditoria_de_creacion(client):
    token = _token(client)
    creada = _crear_esmeralda(client, token).json()
    assert creada["creado_en"] is not None
    assert creada["creado_por"] is not None  # id del usuario admin autenticado
    assert creada["actualizado_en"] is None
    assert creada["actualizado_por"] is None


# --- Optimistic Locking ---


def test_actualizar_esmeralda_con_version_correcta(client):
    token = _token(client)
    creada = _crear_esmeralda(client, token).json()

    resp = client.put(
        f"{ESM}/{creada['id']}",
        json={
            "mina_origen": "Chivor",
            "quilates": 3.0,
            "version": 1,
            "motivo": "Corrección de mina de origen",
        },
        headers=_headers(token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["mina_origen"] == "Chivor"
    assert body["version"] == 2
    assert body["actualizado_por"] is not None


def test_actualizar_esmeralda_con_version_desactualizada_devuelve_422(client):
    token = _token(client)
    creada = _crear_esmeralda(client, token).json()

    # Primera actualización exitosa (version 1 -> 2)
    client.put(
        f"{ESM}/{creada['id']}",
        json={"mina_origen": "Chivor", "quilates": 3.0, "version": 1},
        headers=_headers(token),
    )

    # Segunda actualización reutilizando la version vieja (1) debe fallar
    resp = client.put(
        f"{ESM}/{creada['id']}",
        json={"mina_origen": "Coscuez", "quilates": 1.0, "version": 1},
        headers=_headers(token),
    )
    assert resp.status_code == 422
    assert "modificada" in resp.json()["detail"].lower() or "versión" in resp.json()["detail"].lower()


def test_actualizaciones_concurrentes_secuenciales_incrementan_version(client):
    token = _token(client)
    creada = _crear_esmeralda(client, token).json()

    r1 = client.put(
        f"{ESM}/{creada['id']}",
        json={"mina_origen": "Chivor", "quilates": 2.5, "version": 1},
        headers=_headers(token),
    )
    assert r1.json()["version"] == 2

    r2 = client.put(
        f"{ESM}/{creada['id']}",
        json={"mina_origen": "Coscuez", "quilates": 2.7, "version": 2},
        headers=_headers(token),
    )
    assert r2.json()["version"] == 3


# --- Baja lógica ---


def test_desactivar_esmeralda_es_baja_logica(client):
    token = _token(client)
    creada = _crear_esmeralda(client, token).json()

    resp = client.delete(f"{ESM}/{creada['id']}", headers=_headers(token))
    assert resp.status_code == 200

    # Sigue existiendo (no fue un DELETE físico), pero no aparece en el listado por defecto
    resp_get = client.get(f"{ESM}/{creada['id']}", headers=_headers(token))
    assert resp_get.status_code == 200

    resp_listado = client.get(f"{ESM}", headers=_headers(token))
    ids_listados = [e["id"] for e in resp_listado.json()["items"]]
    assert creada["id"] not in ids_listados


# --- Filtros y paginación ---


def test_listar_con_filtro_por_mina_origen(client):
    token = _token(client)
    _crear_esmeralda(client, token, mina_origen="Muzo")
    _crear_esmeralda(client, token, mina_origen="Chivor")

    resp = client.get(f"{ESM}?mina_origen=Chivor", headers=_headers(token))
    body = resp.json()
    assert all(e["mina_origen"] == "Chivor" for e in body["items"])


def test_listar_con_filtro_por_rango_de_quilates(client):
    token = _token(client)
    _crear_esmeralda(client, token, quilates=1.0)
    _crear_esmeralda(client, token, quilates=5.0)

    resp = client.get(f"{ESM}?quilates_min=4&quilates_max=6", headers=_headers(token))
    body = resp.json()
    assert all(4 <= e["quilates"] <= 6 for e in body["items"])


# --- Regresión: JoyaService (Etapa 7) sigue funcionando igual (ADR-008-02) ---


def test_regresion_joya_service_valida_esmeralda_completada_correctamente(client):
    token = _token(client)
    esmeralda = _crear_esmeralda(client, token).json()

    resp_joya = client.post(
        JOY,
        json={
            "referencia": f"TR-REG-{uuid.uuid4().hex[:8]}",
            "nombre": "Anillo de Regresión",
            "tipo": "anillo",
            "esmeralda_id": esmeralda["id"],
        },
        headers=_headers(token),
    )
    assert resp_joya.status_code == 201
    assert resp_joya.json()["esmeralda_id"] == esmeralda["id"]


def test_regresion_esmeralda_ya_vinculada_sigue_bloqueando_segunda_joya(client):
    token = _token(client)
    esmeralda = _crear_esmeralda(client, token).json()

    client.post(
        JOY,
        json={
            "referencia": f"TR-REG-A-{uuid.uuid4().hex[:8]}",
            "nombre": "Joya A",
            "tipo": "anillo",
            "esmeralda_id": esmeralda["id"],
        },
        headers=_headers(token),
    )
    resp_segunda = client.post(
        JOY,
        json={
            "referencia": f"TR-REG-B-{uuid.uuid4().hex[:8]}",
            "nombre": "Joya B",
            "tipo": "collar",
            "esmeralda_id": esmeralda["id"],
        },
        headers=_headers(token),
    )
    assert resp_segunda.status_code == 409
