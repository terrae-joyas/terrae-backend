"""Modelos ORM de trazabilidad transversal: auditoría de seguridad,
historial de negocio y logs técnicos del sistema.

Distinción deliberada entre las tres tablas:
- `AuditoriaModel`: quién hizo qué acción sensible en el sistema
  (seguridad/cumplimiento) — ej. "Juan cambió el rol de María a auditor".
- `HistorialEventoModel`: la línea de tiempo de negocio de una entidad
  (ej. una joya) — ej. "Cambio de propietario", "Certificado revocado".
- `LogSistemaModel`: eventos técnicos (errores, resultados de inferencia
  de IA, fallos de integración blockchain) para diagnóstico operativo.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class AuditoriaModel(Base):
    __tablename__ = "auditorias"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    usuario_id: Mapped[str | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    accion: Mapped[str] = mapped_column(String(120), nullable=False)
    entidad_tipo: Mapped[str] = mapped_column(String(60), nullable=False)
    entidad_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    ip_origen: Mapped[str | None] = mapped_column(String(45), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class HistorialEventoModel(Base):
    __tablename__ = "historial_eventos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    entidad_tipo: Mapped[str] = mapped_column(String(60), nullable=False)  # ej. "joya"
    entidad_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    evento: Mapped[str] = mapped_column(String(120), nullable=False)
    detalle: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    ocurrido_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class LogSistemaModel(Base):
    __tablename__ = "logs_sistema"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nivel: Mapped[str] = mapped_column(String(20), nullable=False, default="info")
    # info | warning | error | critical
    origen: Mapped[str] = mapped_column(String(80), nullable=False)  # ej. "ia.inferencia", "blockchain.gateway"
    mensaje: Mapped[str] = mapped_column(String(2000), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
