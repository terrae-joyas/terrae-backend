"""Modelos ORM: usuarios y permisos.

`UsuarioModel` es la contraparte persistente de la entidad de dominio
`Usuario` (app/domain/entities/user.py). El mapeo entre ambos vive en
`PostgresUsuarioRepository`, nunca aquí ni en el dominio.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nombre_completo: Mapped[str] = mapped_column(String(120), nullable=False)
    correo: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(20), nullable=False, default="cliente")
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    cliente = relationship("ClienteModel", back_populates="usuario", uselist=False)


class PermisoModel(Base):
    """Catálogo de permisos granulares (ej. 'joyas.crear', 'certificados.emitir').

    En esta etapa el control de acceso sigue basándose en `UsuarioModel.rol`
    (ver Etapa 4); esta tabla deja preparada la extensión a permisos
    granulares por rol sin requerir otro cambio de esquema.
    """

    __tablename__ = "permisos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False)


class RolPermisoModel(Base):
    """Asociación rol → permiso (muchos a muchos)."""

    __tablename__ = "rol_permisos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    permiso_id: Mapped[int] = mapped_column(
        ForeignKey("permisos.id", ondelete="CASCADE"), nullable=False
    )
