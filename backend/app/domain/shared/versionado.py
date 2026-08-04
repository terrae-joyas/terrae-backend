"""
Campos de versionado (Etapa 8 — ADR-008-01).

`CamposVersion` complementa a `CamposAuditoria` (Etapa 7.5). Se separan
en dos mixins distintos porque no toda entidad con auditoría necesita
necesariamente versionado explícito en el dominio (aunque desde la
Etapa 8 el mandato es que sí, para toda entidad nueva) — mantenerlos
desacoplados respeta el Principio de Segregación de Interfaces (SOLID).

El `motivo` de un cambio NO es un campo de este mixin: pertenece al
comando de actualización (DTO), no al estado persistente de la
entidad — se registra vía `RegistradorVersion` (Etapa 7.5,
`app/infrastructure/events/version_registry.py`), reutilizando
`historial_eventos`.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(kw_only=True)
class CamposVersion:
    version: int = 1
