"""DTOs del recurso Esmeralda (Etapa 8)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.entities.esmeralda import MinaOrigen


class EsmeraldaCreateRequest(BaseModel):
    codigo_interno: str = Field(min_length=3, max_length=40)
    mina_origen: MinaOrigen
    quilates: float = Field(gt=0, le=500)
    color: str | None = Field(default=None, max_length=60)
    claridad: str | None = Field(default=None, max_length=60)
    corte: str | None = Field(default=None, max_length=60)
    tratamientos: str | None = Field(default=None, max_length=255)
    tipo_inclusion_principal: str | None = Field(default=None, max_length=120)


class EsmeraldaUpdateRequest(BaseModel):
    """Incluye `version` (Optimistic Locking, ADR-008-04) y `motivo`
    (Versionado, ADR-008-01) — este último no se persiste en la
    entidad, se registra vía `RegistradorVersion` (Etapa 7.5)."""

    mina_origen: MinaOrigen
    quilates: float = Field(gt=0, le=500)
    color: str | None = Field(default=None, max_length=60)
    claridad: str | None = Field(default=None, max_length=60)
    corte: str | None = Field(default=None, max_length=60)
    tratamientos: str | None = Field(default=None, max_length=255)
    tipo_inclusion_principal: str | None = Field(default=None, max_length=120)
    version: int = Field(description="Versión que el cliente cree tener; debe coincidir con la actual")
    motivo: str | None = Field(default=None, max_length=255, description="Motivo del cambio, para auditoría")


class EsmeraldaResponse(BaseModel):
    id: str
    codigo_interno: str
    mina_origen: MinaOrigen
    quilates: float
    color: str | None
    claridad: str | None
    corte: str | None
    tratamientos: str | None
    tipo_inclusion_principal: str | None
    version: int
    creado_en: datetime | None
    actualizado_en: datetime | None
    creado_por: str | None
    actualizado_por: str | None
