"""DTOs del recurso Inventario (Etapa 9)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class InventarioCreateRequest(BaseModel):
    joya_id: str
    sucursal_id: str
    cantidad: int = Field(default=1, ge=0)
    ubicacion_fisica: str | None = Field(default=None, max_length=120)


class InventarioMoverRequest(BaseModel):
    """Cambia sucursal/ubicación física. NO ajusta `cantidad` — ver
    `InventarioAjustarCantidadRequest` y ADR-009-01."""

    sucursal_id: str
    ubicacion_fisica: str | None = Field(default=None, max_length=120)
    version: int = Field(description="Versión que el cliente cree tener; debe coincidir con la actual")


class InventarioAjustarCantidadRequest(BaseModel):
    """`delta` puede ser negativo (salida) o positivo (entrada).
    `motivo` es obligatorio (ADR-009-01) — a diferencia de Esmeralda,
    un movimiento de inventario sin motivo es deuda de auditoría
    inaceptable."""

    delta: int = Field(description="Cambio a aplicar; negativo = salida, positivo = entrada")
    motivo: str = Field(min_length=3, max_length=255)
    version: int = Field(description="Versión que el cliente cree tener; debe coincidir con la actual")


class InventarioResponse(BaseModel):
    id: str
    joya_id: str
    sucursal_id: str
    cantidad: int
    ubicacion_fisica: str | None
    version: int
    creado_en: datetime | None
    actualizado_en: datetime | None
    creado_por: str | None
    actualizado_por: str | None
