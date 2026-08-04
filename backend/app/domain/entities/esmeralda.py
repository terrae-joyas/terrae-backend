"""Entidad de dominio: Esmeralda.

Completada en la Etapa 8 (ver ADR-008-02): hereda `CamposAuditoria`
(Etapa 7.5) y `CamposVersion` (Etapa 8) por mandato de
`CONSTITUCION_INGENIERIA_TERRAE.md` §4 — toda entidad nueva desde la
Etapa 8 implementa auditoría y versionado. La Etapa 7 la había dejado
parcial (sin estos campos) porque en ese momento solo se necesitaba
verificar existencia; esto NO es "reescribir un módulo finalizado":
está documentado desde la Etapa 7 que la Etapa 8 la completaría.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

from app.domain.shared.auditoria import CamposAuditoria
from app.domain.shared.versionado import CamposVersion


class MinaOrigen(str, Enum):
    MUZO = "Muzo"
    CHIVOR = "Chivor"
    COSCUEZ = "Coscuez"


@dataclass(kw_only=True)
class Esmeralda(CamposAuditoria, CamposVersion):
    codigo_interno: str
    mina_origen: MinaOrigen
    quilates: float
    color: str | None = None
    claridad: str | None = None
    corte: str | None = None
    tratamientos: str | None = None
    tipo_inclusion_principal: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
