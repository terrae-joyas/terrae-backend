"""Modelo ORM: certificados digitales (Pasaporte Digital / Etapa 10).

Completado en la Etapa 10 con versionado y auditoría parcial — ver
ADR-010-02: `emitido_por`/`emitido_en` (Etapa 5) se conservan tal cual
(equivalentes de dominio a `creado_por`/`creado_en`, con nombre propio
por significado legal/de negocio), y se agregan
`actualizado_en`/`actualizado_por`/`eliminado_en`/`eliminado_por`
(mismos tipos que `AuditoriaMixin`, sin heredarlo para evitar colisión
de nombres) más `VersionadoMixin` (`version`), que sí se reutiliza sin
conflicto.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.db.mixins import VersionadoMixin


class CertificadoModel(Base, VersionadoMixin):
    __tablename__ = "certificados"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    numero_certificado: Mapped[str] = mapped_column(
        String(40), nullable=False, unique=True, index=True
    )
    joya_id: Mapped[str] = mapped_column(ForeignKey("joyas.id", ondelete="CASCADE"), nullable=False)
    hash_sha256: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    emitido_por: Mapped[str | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="emitido")
    # emitido | revocado | en_revision
    emitido_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # --- Auditoría parcial (ADR-010-02) ---
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    actualizado_por: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    eliminado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    eliminado_por: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )

    joya = relationship("JoyaModel", back_populates="certificados")
    registro_blockchain: Mapped["RegistroBlockchainModel | None"] = relationship(
        back_populates="certificado", uselist=False
    )
    qr: Mapped["QRModel | None"] = relationship(back_populates="certificado", uselist=False)
