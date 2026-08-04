"""Modelos ORM comerciales: clientes, historial de propietarios, ventas,
garantías y mantenimientos."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class ClienteModel(Base):
    """Perfil comercial de un cliente. Puede o no tener cuenta de acceso
    (`usuario_id` nulo = cliente registrado solo en punto de venta, sin
    login al Pasaporte Digital todavía)."""

    __tablename__ = "clientes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    usuario_id: Mapped[str | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, unique=True
    )
    nombre_completo: Mapped[str] = mapped_column(String(120), nullable=False)
    correo_contacto: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefono_contacto: Mapped[str | None] = mapped_column(String(30), nullable=True)
    documento_identidad: Mapped[str | None] = mapped_column(String(40), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    usuario = relationship("UsuarioModel", back_populates="cliente")
    ventas: Mapped[list["VentaModel"]] = relationship(back_populates="cliente")
    propiedades: Mapped[list["PropietarioHistorialModel"]] = relationship(back_populates="cliente")


class PropietarioHistorialModel(Base):
    """Cadena de custodia de una joya: quién la ha poseído y desde cuándo.
    Distinto de `ClienteModel` (perfil comercial) — un propietario
    histórico puede no ser cliente activo (ej. una herencia, una reventa
    fuera de Terrae registrada manualmente)."""

    __tablename__ = "historial_propietarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    joya_id: Mapped[str] = mapped_column(ForeignKey("joyas.id", ondelete="CASCADE"), nullable=False)
    cliente_id: Mapped[str | None] = mapped_column(
        ForeignKey("clientes.id", ondelete="SET NULL"), nullable=True
    )
    nombre_propietario: Mapped[str] = mapped_column(String(120), nullable=False)
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_fin: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    cliente = relationship("ClienteModel", back_populates="propiedades")


class VentaModel(Base):
    __tablename__ = "ventas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    joya_id: Mapped[str] = mapped_column(ForeignKey("joyas.id", ondelete="RESTRICT"), nullable=False)
    cliente_id: Mapped[str] = mapped_column(
        ForeignKey("clientes.id", ondelete="RESTRICT"), nullable=False
    )
    sucursal_id: Mapped[str | None] = mapped_column(
        ForeignKey("sucursales.id", ondelete="SET NULL"), nullable=True
    )
    precio: Mapped[float] = mapped_column(Float, nullable=False)
    moneda: Mapped[str] = mapped_column(String(10), nullable=False, default="COP")
    fecha_venta: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    cliente = relationship("ClienteModel", back_populates="ventas")
    garantia: Mapped["GarantiaModel | None"] = relationship(back_populates="venta", uselist=False)


class GarantiaModel(Base):
    __tablename__ = "garantias"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    venta_id: Mapped[str] = mapped_column(
        ForeignKey("ventas.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_fin: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    condiciones: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="vigente")
    # vigente | vencida | anulada

    venta = relationship("VentaModel", back_populates="garantia")


class MantenimientoModel(Base):
    """Servicio técnico realizado a una joya (limpieza, ajuste, reemplazo
    de engaste, etc.), parte del historial post-venta."""

    __tablename__ = "mantenimientos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    joya_id: Mapped[str] = mapped_column(ForeignKey("joyas.id", ondelete="CASCADE"), nullable=False)
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    tecnico_responsable: Mapped[str | None] = mapped_column(String(120), nullable=True)
    sucursal_id: Mapped[str | None] = mapped_column(
        ForeignKey("sucursales.id", ondelete="SET NULL"), nullable=True
    )
