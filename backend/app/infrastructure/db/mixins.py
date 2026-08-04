"""
Mixins de SQLAlchemy para columnas transversales (Etapa 7.5).

`AuditoriaMixin` y `VersionadoMixin` son mixins de clase (no modelos en
sí) pensados para que los modelos ORM de las etapas 8 en adelante los
incluyan por herencia múltiple junto a `Base`:

    class EsmeraldaModel(Base, AuditoriaMixin, VersionadoMixin):
        __tablename__ = "esmeraldas_v2"
        ...

Al ser mixins de `sqlalchemy.orm.DeclarativeBase`, cada modelo que los
use obtiene sus propias columnas físicas en SU tabla — no crean tablas
ni columnas por sí solos. Por eso agregarlos aquí no modifica ninguna
tabla existente ni requiere una migración hasta que un modelo nuevo los
adopte.

NO se aplican retroactivamente a `UsuarioModel`, `SucursalModel`,
`JoyaModel` ni `EsmeraldaModel` en esta etapa — ver justificación en
`app/domain/shared/auditoria.py` y en
`docs/ETAPA_7_5_ARQUITECTURA_EMPRESARIAL.md`.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column


class AuditoriaMixin:
    """Columnas de auditoría estándar. `creado_por`/`actualizado_por`/
    `eliminado_por` son FK a `usuarios.id` (nullable: acciones del
    sistema, como la siembra de datos, no tienen usuario asociado)."""

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    creado_por: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    actualizado_por: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    eliminado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    eliminado_por: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )


class VersionadoMixin:
    """Columna de versión para optimistic locking (preparación — ver
    `app/application/concurrencia.py` para el mecanismo de verificación,
    todavía no aplicado a ninguna entidad existente)."""

    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
