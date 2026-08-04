"""DTOs del recurso Joya."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.entities.joya import EstadoJoya, TipoJoya


class JoyaCreateRequest(BaseModel):
    referencia: str = Field(min_length=3, max_length=40)
    nombre: str = Field(min_length=2, max_length=120)
    tipo: TipoJoya
    material_metal: str | None = Field(default=None, max_length=60)
    esmeralda_id: str | None = None
    sucursal_id: str | None = None


class JoyaUpdateRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    tipo: TipoJoya
    material_metal: str | None = Field(default=None, max_length=60)
    esmeralda_id: str | None = None
    sucursal_id: str | None = None


class CambiarEstadoRequest(BaseModel):
    nuevo_estado: EstadoJoya


class JoyaResponse(BaseModel):
    id: str
    referencia: str
    nombre: str
    tipo: TipoJoya
    material_metal: str | None
    estado: EstadoJoya
    esmeralda_id: str | None
    sucursal_id: str | None
    creado_en: datetime
