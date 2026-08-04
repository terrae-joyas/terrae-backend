"""Entidad de dominio: ActivoMultimedia (Etapa 10).

Ver ADR-010-01: entidad polimórfica transversal para todo archivo
multimedia trazable (fotografía, imagen microscópica, certificado
escaneado, recurso visual), sustituyendo a `FotografiaModel` (Etapa 5,
sin consumidores).

De los 6 metadatos exigidos (autor, fecha, dispositivo, versión, hash,
relación), 4 los resuelve `CamposAuditoria`/`CamposVersion` ya
heredados: `creado_por` = autor, `creado_en` = fecha, `version` =
versión. Solo `dispositivo` y `hash_sha256` son campos propios nuevos.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

from app.domain.shared.auditoria import CamposAuditoria
from app.domain.shared.versionado import CamposVersion

_PATRON_SHA256 = re.compile(r"^[a-f0-9]{64}$")


class TipoActivoMultimedia(str, Enum):
    FOTO_JOYA = "foto_joya"
    IMAGEN_MICROSCOPICA = "imagen_microscopica"
    CERTIFICADO_ESCANEADO = "certificado_escaneado"
    RECURSO_VISUAL = "recurso_visual"


class HashInvalidoError(ValueError):
    pass


@dataclass(kw_only=True)
class ActivoMultimedia(CamposAuditoria, CamposVersion):
    entidad_tipo: str  # ej. "Joya", "Esmeralda", "Certificado"
    entidad_id: str
    tipo: TipoActivoMultimedia
    url: str
    hash_sha256: str
    dispositivo: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        hash_normalizado = self.hash_sha256.strip().lower()
        if not _PATRON_SHA256.match(hash_normalizado):
            raise HashInvalidoError(
                "hash_sha256 debe ser un hash SHA-256 válido (64 caracteres hexadecimales)"
            )
        self.hash_sha256 = hash_normalizado
