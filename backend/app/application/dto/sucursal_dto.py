"""DTOs del recurso Sucursal."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.entities.sucursal import TipoSucursal


class SucursalCreateRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    tipo: TipoSucursal
    ciudad: str = Field(min_length=2, max_length=80)
    direccion: str | None = Field(default=None, max_length=255)


class SucursalUpdateRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    tipo: TipoSucursal
    ciudad: str = Field(min_length=2, max_length=80)
    direccion: str | None = Field(default=None, max_length=255)
    activa: bool = True


class SucursalResponse(BaseModel):
    id: str
    nombre: str
    tipo: TipoSucursal
    ciudad: str
    direccion: str | None
    activa: bool
    creado_en: datetime
