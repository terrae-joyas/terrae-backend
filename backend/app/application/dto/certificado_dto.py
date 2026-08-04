"""DTOs del recurso Certificado (Etapa 10)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.entities.certificado import EstadoCertificado


class CertificadoEmitirRequest(BaseModel):
    joya_id: str


class CertificadoRevocarRequest(BaseModel):
    version: int = Field(description="Versión que el cliente cree tener; debe coincidir con la actual")
    motivo: str = Field(min_length=3, max_length=255)


class CertificadoResponse(BaseModel):
    id: str
    numero_certificado: str
    joya_id: str
    hash_sha256: str
    emitido_por: str | None
    estado: EstadoCertificado
    emitido_en: datetime
    actualizado_en: datetime | None
    actualizado_por: str | None
    version: int
