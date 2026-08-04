"""Entidad de dominio: Inventario (Etapa 9).

Primera entidad completamente nueva bajo el régimen obligatorio de
`CONSTITUCION_INGENIERIA_TERRAE.md` §4 (no "completada" desde una
versión parcial, como Esmeralda en la Etapa 8 — Inventario nace ya así).
Relación 1:1 con `Joya`, ya modelada desde la Etapa 5.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from app.domain.shared.auditoria import CamposAuditoria
from app.domain.shared.versionado import CamposVersion


@dataclass(kw_only=True)
class Inventario(CamposAuditoria, CamposVersion):
    joya_id: str
    sucursal_id: str
    cantidad: int = 1
    ubicacion_fisica: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
