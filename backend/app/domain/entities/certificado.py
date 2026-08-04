"""Entidad de dominio: Certificado digital (Etapa 10).

Ver ADR-010-02: NO hereda `CamposAuditoria` (evitaría colisión de
nombres con `emitido_en`/`emitido_por`, semánticamente equivalentes
pero con nombre de dominio propio). Sí hereda `CamposVersion`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from app.domain.shared.versionado import CamposVersion


class EstadoCertificado(str, Enum):
    EMITIDO = "emitido"
    REVOCADO = "revocado"
    EN_REVISION = "en_revision"


@dataclass(kw_only=True)
class Certificado(CamposVersion):
    numero_certificado: str
    joya_id: str
    hash_sha256: str
    emitido_por: str | None = None
    estado: EstadoCertificado = EstadoCertificado.EMITIDO
    emitido_en: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    actualizado_en: datetime | None = None
    actualizado_por: str | None = None
    eliminado_en: datetime | None = None
    eliminado_por: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))

    def puede_revocarse(self) -> bool:
        return self.estado == EstadoCertificado.EMITIDO
