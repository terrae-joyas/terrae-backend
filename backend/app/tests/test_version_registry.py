"""Pruebas de HistorialEventoRegistradorVersion (Etapa 7.5).

Usa SQLite en memoria, mismo patrón que test_postgres_user_repository.py
y test_auditoria_infra.py — válido porque HistorialEventoModel solo usa
tipos de columna estándar de SQLAlchemy.
"""

from __future__ import annotations

import json

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.auditoria import HistorialEventoModel

# Importa todos los modelos reales antes de crear las tablas.
import app.infrastructure.db.models  # noqa: F401
from app.infrastructure.events.version_registry import HistorialEventoRegistradorVersion


@pytest.fixture()
def registrador():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine, tables=[HistorialEventoModel.__table__])
    session_factory = sessionmaker(bind=engine, future=True)
    yield HistorialEventoRegistradorVersion(session_factory), session_factory
    engine.dispose()


def test_registrar_version_crea_fila_en_historial_eventos(registrador):
    reg, session_factory = registrador
    reg.registrar_version(
        entidad_tipo="Sucursal",
        entidad_id="s-1",
        version=2,
        usuario_id="user-1",
        motivo="corrección de dirección",
    )

    with session_factory() as session:
        filas = session.scalars(select(HistorialEventoModel)).all()

    assert len(filas) == 1
    assert filas[0].entidad_tipo == "Sucursal"
    assert filas[0].entidad_id == "s-1"
    assert filas[0].evento == "version_registrada"


def test_detalle_almacena_version_usuario_y_motivo_como_json(registrador):
    reg, session_factory = registrador
    reg.registrar_version(
        entidad_tipo="Joya", entidad_id="j-1", version=5, usuario_id="user-2", motivo="cambio de estado"
    )

    with session_factory() as session:
        fila = session.scalars(select(HistorialEventoModel)).one()

    detalle = json.loads(fila.detalle)
    assert detalle == {"version": 5, "usuario_id": "user-2", "motivo": "cambio de estado"}


def test_registrar_version_sin_motivo_es_valido(registrador):
    reg, session_factory = registrador
    reg.registrar_version(entidad_tipo="Joya", entidad_id="j-2", version=1, usuario_id=None)

    with session_factory() as session:
        fila = session.scalars(select(HistorialEventoModel)).one()

    detalle = json.loads(fila.detalle)
    assert detalle["motivo"] is None
    assert detalle["usuario_id"] is None


def test_multiples_registros_para_la_misma_entidad_se_acumulan(registrador):
    reg, session_factory = registrador
    reg.registrar_version(entidad_tipo="Joya", entidad_id="j-3", version=1, usuario_id="u1")
    reg.registrar_version(entidad_tipo="Joya", entidad_id="j-3", version=2, usuario_id="u1")

    with session_factory() as session:
        filas = session.scalars(
            select(HistorialEventoModel).where(HistorialEventoModel.entidad_id == "j-3")
        ).all()

    assert len(filas) == 2
