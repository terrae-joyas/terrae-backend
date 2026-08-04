"""Modelo ORM: activos multimedia trazables (Etapa 10, ADR-010-01).

Sustituye a `FotografiaModel` (Etapa 5, sin consumidores) con una
entidad polimórfica que cubre cualquier archivo multimedia asociado a
cualquier entidad de negocio (Joya, Esmeralda, Certificado, etc.),
con metadatos completos de trazabilidad.
"""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base
from app.infrastructure.db.mixins import AuditoriaMixin, VersionadoMixin


class ActivoMultimediaModel(Base, AuditoriaMixin, VersionadoMixin):
    __tablename__ = "activos_multimedia"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    entidad_tipo: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    entidad_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    # foto_joya | imagen_microscopica | certificado_escaneado | recurso_visual
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    hash_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    dispositivo: Mapped[str] = mapped_column(String(120), nullable=True)
