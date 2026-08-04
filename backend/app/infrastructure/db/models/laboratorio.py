"""Modelos ORM del laboratorio SIEGEM Lab: equipos, calibraciones y capturas
usadas por el pipeline de IA de certificación gemológica (Etapa 13)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class MicroscopioModel(Base):
    """Equipo físico de captura (microscopio digital / cámara macro)."""

    __tablename__ = "microscopios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    codigo_equipo: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    modelo: Mapped[str] = mapped_column(String(120), nullable=False)
    sucursal_id: Mapped[str | None] = mapped_column(
        ForeignKey("sucursales.id", ondelete="SET NULL"), nullable=True
    )
    en_servicio: Mapped[bool] = mapped_column(default=True)

    calibraciones: Mapped[list["CalibracionModel"]] = relationship(back_populates="microscopio")
    capturas: Mapped[list["CapturaModel"]] = relationship(back_populates="microscopio")


class CalibracionModel(Base):
    """Registro de calibración periódica de un microscopio (trazabilidad
    metrológica exigida por el pipeline de certificación)."""

    __tablename__ = "calibraciones"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    microscopio_id: Mapped[str] = mapped_column(
        ForeignKey("microscopios.id", ondelete="CASCADE"), nullable=False
    )
    fecha_calibracion: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    responsable: Mapped[str] = mapped_column(String(120), nullable=False)
    resultado: Mapped[str] = mapped_column(String(30), nullable=False, default="aprobada")
    observaciones: Mapped[str] = mapped_column(String(500), nullable=True)

    microscopio: Mapped[MicroscopioModel] = relationship(back_populates="calibraciones")


class CapturaModel(Base):
    """Captura de imagen de una esmeralda/joya para el pipeline de IA
    (detección de inclusiones, clasificación de origen, etc.)."""

    __tablename__ = "capturas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    esmeralda_id: Mapped[str | None] = mapped_column(
        ForeignKey("esmeraldas.id", ondelete="SET NULL"), nullable=True
    )
    microscopio_id: Mapped[str | None] = mapped_column(
        ForeignKey("microscopios.id", ondelete="SET NULL"), nullable=True
    )
    imagen_url: Mapped[str] = mapped_column(String(500), nullable=False)
    aumento_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    modelo_ia_usado: Mapped[str] = mapped_column(String(80), nullable=True)
    resultado_json: Mapped[str] = mapped_column(String, nullable=True)  # payload serializado del modelo
    capturado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    esmeralda: Mapped["EsmeraldaModel | None"] = relationship(back_populates="capturas")
    microscopio: Mapped[MicroscopioModel | None] = relationship(back_populates="capturas")
