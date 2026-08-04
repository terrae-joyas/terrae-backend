"""
Pruebas de `PostgresUsuarioRepository`.

Usa SQLite en memoria como motor de pruebas en vez de PostgreSQL real:
es válido porque todos los tipos de columna usados en los modelos
(`String`, `Boolean`, `DateTime`, `Float`, `Integer`) son estándar de
SQLAlchemy y se comportan igual en ambos motores — no se usa ningún
tipo específico de PostgreSQL (JSONB, ARRAY, UUID nativo) que requeriría
una prueba de integración aparte contra PostgreSQL real (ver
`docs/ETAPA_5_BASE_DE_DATOS.md`, sección de validación pendiente).
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.entities.user import RolUsuario, Usuario
from app.infrastructure.db.base import Base

# Importa todos los modelos para que Base.metadata los conozca.
import app.infrastructure.db.models  # noqa: F401
from app.infrastructure.repositories.postgres_user_repository import PostgresUsuarioRepository
from app.infrastructure.security.password_hasher import hash_password


@pytest.fixture()
def repo():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, future=True)
    yield PostgresUsuarioRepository(session_factory)
    engine.dispose()


def _usuario_de_prueba(correo="test@terrae.co", rol=RolUsuario.CLIENTE) -> Usuario:
    return Usuario(
        nombre_completo="Usuario de Prueba",
        correo=correo,
        hashed_password=hash_password("Password123"),
        rol=rol,
    )


def test_crear_y_obtener_por_id(repo):
    usuario = _usuario_de_prueba()
    repo.crear(usuario)

    encontrado = repo.obtener_por_id(usuario.id)
    assert encontrado is not None
    assert encontrado.correo == usuario.correo
    assert encontrado.rol == RolUsuario.CLIENTE


def test_obtener_por_correo_es_case_insensitive(repo):
    usuario = _usuario_de_prueba(correo="mayuscula@terrae.co")
    repo.crear(usuario)

    encontrado = repo.obtener_por_correo("MAYUSCULA@Terrae.co")
    assert encontrado is not None
    assert encontrado.id == usuario.id


def test_obtener_por_id_inexistente_devuelve_none(repo):
    assert repo.obtener_por_id("no-existe") is None


def test_listar_todos_devuelve_todos_los_usuarios_creados(repo):
    repo.crear(_usuario_de_prueba(correo="a@terrae.co"))
    repo.crear(_usuario_de_prueba(correo="b@terrae.co"))

    todos = repo.listar_todos()
    assert len(todos) == 2
    correos = {u.correo for u in todos}
    assert correos == {"a@terrae.co", "b@terrae.co"}


def test_actualizar_persiste_cambios(repo):
    usuario = _usuario_de_prueba(correo="actualizar@terrae.co")
    repo.crear(usuario)

    usuario.rol = RolUsuario.ADMINISTRADOR
    usuario.activo = False
    repo.actualizar(usuario)

    actualizado = repo.obtener_por_id(usuario.id)
    assert actualizado.rol == RolUsuario.ADMINISTRADOR
    assert actualizado.activo is False


def test_actualizar_usuario_inexistente_lanza_error(repo):
    usuario = _usuario_de_prueba()
    with pytest.raises(ValueError):
        repo.actualizar(usuario)


def test_sembrar_si_vacio_solo_siembra_una_vez(repo):
    semilla = [_usuario_de_prueba(correo="semilla1@terrae.co"), _usuario_de_prueba(correo="semilla2@terrae.co")]
    repo.sembrar_si_vacio(semilla)
    assert len(repo.listar_todos()) == 2

    # Segunda llamada no debe duplicar ni fallar
    repo.sembrar_si_vacio([_usuario_de_prueba(correo="otra@terrae.co")])
    assert len(repo.listar_todos()) == 2
