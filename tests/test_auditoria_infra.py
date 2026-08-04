"""Pruebas de la infraestructura de auditoría (Etapa 7.5)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import String, create_engine
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.domain.shared.auditoria import CamposAuditoria
from app.infrastructure.db.base import Base
from app.infrastructure.db.mixins import AuditoriaMixin, VersionadoMixin

# Importa todos los modelos reales para que "usuarios" (referenciada por
# las FK de AuditoriaMixin) exista en Base.metadata al crear la tabla
# de prueba — mismo patrón que test_postgres_user_repository.py.
import app.infrastructure.db.models  # noqa: F401


# --- Dominio: CamposAuditoria ---


@dataclass(kw_only=True)
class _EntidadDePrueba(CamposAuditoria):
    nombre: str


def test_campos_auditoria_todos_opcionales_por_defecto():
    entidad = _EntidadDePrueba(nombre="prueba")
    assert entidad.creado_en is None
    assert entidad.actualizado_en is None
    assert entidad.creado_por is None
    assert entidad.eliminado_en is None
    assert entidad.esta_eliminado is False


def test_campos_auditoria_esta_eliminado_true_cuando_hay_eliminado_en():
    entidad = _EntidadDePrueba(
        nombre="prueba", eliminado_en=datetime.now(timezone.utc), eliminado_por="user-1"
    )
    assert entidad.esta_eliminado is True


def test_campos_auditoria_se_puede_combinar_con_campos_propios():
    entidad = _EntidadDePrueba(
        nombre="prueba",
        creado_en=datetime.now(timezone.utc),
        creado_por="user-1",
    )
    assert entidad.nombre == "prueba"
    assert entidad.creado_por == "user-1"


# --- Infraestructura: AuditoriaMixin / VersionadoMixin (SQLite en memoria) ---
# Modelo de prueba local (no forma parte del esquema real de Terrae;
# no se agrega a app/infrastructure/db/models/__init__.py ni afecta a
# Alembic ni a ninguna tabla existente).


class _ModeloDePrueba(Base, AuditoriaMixin, VersionadoMixin):
    __tablename__ = "modelo_de_prueba_auditoria"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)


def test_mixin_auditoria_y_version_generan_columnas_correctas():
    columnas = {c.name for c in _ModeloDePrueba.__table__.columns}
    assert {
        "id",
        "nombre",
        "creado_en",
        "actualizado_en",
        "creado_por",
        "actualizado_por",
        "eliminado_en",
        "eliminado_por",
        "version",
    }.issubset(columnas)


def test_mixin_persiste_valores_por_defecto():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine, tables=[_ModeloDePrueba.__table__])

    with Session(engine) as session:
        registro = _ModeloDePrueba(id="abc-1", nombre="Test")
        session.add(registro)
        session.commit()

        recuperado = session.get(_ModeloDePrueba, "abc-1")
        assert recuperado is not None
        assert recuperado.version == 1
        assert recuperado.creado_en is not None
        assert recuperado.eliminado_en is None

    engine.dispose()


def test_mixin_foreign_keys_apuntan_a_usuarios():
    fks_creado_por = {
        fk.target_fullname for fk in _ModeloDePrueba.__table__.columns["creado_por"].foreign_keys
    }
    assert fks_creado_por == {"usuarios.id"}
