"""DTOs del recurso ActivoMultimedia (Etapa 10)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.domain.entities.activo_multimedia import TipoActivoMultimedia

_LONGITUD_HASH_SHA256 = 64


class ActivoMultimediaCreateRequest(BaseModel):
    entidad_tipo: str = Field(min_length=2, max_length=60, description='ej. "Joya", "Esmeralda", "Certificado"')
    entidad_id: str
    tipo: TipoActivoMultimedia
    url: str = Field(min_length=5, max_length=500)
    hash_sha256: str = Field(description="Hash SHA-256 del archivo (64 caracteres hexadecimales)")
    dispositivo: str | None = Field(default=None, max_length=120)

    @field_validator("hash_sha256")
    @classmethod
    def validar_formato_hash(cls, v: str) -> str:
        v_normalizado = v.strip().lower()
        if len(v_normalizado) != _LONGITUD_HASH_SHA256 or not all(
            c in "0123456789abcdef" for c in v_normalizado
        ):
            raise ValueError("hash_sha256 debe tener 64 caracteres hexadecimales")
        return v_normalizado


class ActivoMultimediaResponse(BaseModel):
    id: str
    entidad_tipo: str
    entidad_id: str
    tipo: TipoActivoMultimedia
    url: str
    hash_sha256: str
    dispositivo: str | None
    version: int
    creado_en: datetime | None
    actualizado_en: datetime | None
    creado_por: str | None
    actualizado_por: str | None
