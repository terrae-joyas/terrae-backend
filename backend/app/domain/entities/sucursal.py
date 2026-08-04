"""Entidad de dominio: Sucursal (taller, punto de venta o laboratorio)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class TipoSucursal(str, Enum):
    TALLER = "taller"
    PUNTO_VENTA = "punto_venta"
    LABORATORIO = "laboratorio"


@dataclass
class Sucursal:
    nombre: str
    tipo: TipoSucursal
    ciudad: str
    direccion: str | None = None
    activa: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))
    creado_en: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
