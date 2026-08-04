"""Modelos ORM: esmeraldas, joyas e inventario — núcleo gemológico del ecosistema Terrae."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.db.mixins import AuditoriaMixin, VersionadoMixin


class EsmeraldaModel(Base, AuditoriaMixin, VersionadoMixin):
    """Piedra en bruto o tallada, previa a su engaste en una joya.

    Completada en la Etapa 8 (ver ADR-008-02) con `AuditoriaMixin` y
    `VersionadoMixin` (Etapa 7.5) — primera entidad del proyecto en
    adoptarlos, por mandato de `CONSTITUCION_INGENIERIA_TERRAE.md` §4.
    Provee: `creado_en`, `actualizado_en`, `creado_por`,
    `actualizado_por`, `eliminado_en`, `eliminado_por`, `version`.
    """

    __tablename__ = "esmeraldas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    codigo_interno: Mapped[str] = mapped_column(String(40), nullable=False, unique=True, index=True)
    mina_origen: Mapped[str] = mapped_column(String(40), nullable=False)  # Muzo | Chivor | Coscuez
    quilates: Mapped[float] = mapped_column(Float, nullable=False)
    color: Mapped[str] = mapped_column(String(60), nullable=True)
    claridad: Mapped[str] = mapped_column(String(60), nullable=True)
    corte: Mapped[str] = mapped_column(String(60), nullable=True)  # ej. emerald cut, oval, pera
    tratamientos: Mapped[str] = mapped_column(String(255), nullable=True)  # ej. aceite de cedro
    tipo_inclusion_principal: Mapped[str] = mapped_column(String(120), nullable=True)

    joyas: Mapped[list["JoyaModel"]] = relationship(back_populates="esmeralda")
    capturas: Mapped[list["CapturaModel"]] = relationship(back_populates="esmeralda")


class JoyaModel(Base):
    """Pieza terminada de alta joyería (referencia comercial única)."""

    __tablename__ = "joyas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    referencia: Mapped[str] = mapped_column(String(40), nullable=False, unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo: Mapped[str] = mapped_column(String(40), nullable=False)  # anillo | collar | aretes | pulsera
    material_metal: Mapped[str] = mapped_column(String(60), nullable=True)  # oro 18k, platino, etc.
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="en_taller")
    esmeralda_id: Mapped[str | None] = mapped_column(
        ForeignKey("esmeraldas.id", ondelete="SET NULL"), nullable=True
    )
    sucursal_id: Mapped[str | None] = mapped_column(
        ForeignKey("sucursales.id", ondelete="SET NULL"), nullable=True
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    esmeralda: Mapped[EsmeraldaModel | None] = relationship(back_populates="joyas")
    inventario: Mapped["InventarioModel"] = relationship(back_populates="joya", uselist=False)
    certificados: Mapped[list["CertificadoModel"]] = relationship(back_populates="joya")


class InventarioModel(Base, AuditoriaMixin, VersionadoMixin):
    """Existencias de cada joya en su sucursal actual.

    Completada en la Etapa 9 (ver ADR-009-02) con `AuditoriaMixin` y
    `VersionadoMixin` (Etapa 7.5), reemplazando la columna
    `actualizado_en` que ya declaraba manualmente desde la Etapa 5 por
    la equivalente del mixin (mismo nombre, mismo tipo — sin pérdida
    de datos ni migración destructiva).
    """

    __tablename__ = "inventario"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    joya_id: Mapped[str] = mapped_column(
        ForeignKey("joyas.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    sucursal_id: Mapped[str] = mapped_column(
        ForeignKey("sucursales.id", ondelete="RESTRICT"), nullable=False
    )
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    ubicacion_fisica: Mapped[str] = mapped_column(String(120), nullable=True)  # ej. vitrina 3, caja fuerte

    joya: Mapped[JoyaModel] = relationship(back_populates="inventario")
