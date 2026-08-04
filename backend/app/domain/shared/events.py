"""
Domain Events (Etapa 7.5 — infraestructura, sin consumidores todavía).

Un `DomainEvent` describe algo que YA ocurrió en el dominio (tiempo
pasado, inmutable). Los eventos genéricos de aquí abajo
(`EntidadCreadaEvent`, `EntidadActualizadaEvent`,
`EntidadDesactivadaEvent`) cubren el caso común de cualquier entidad;
una entidad con reglas de negocio ricas (como `Joya`) puede definir
eventos propios más específicos (ej. `JoyaMarcadaComoDisponibleEvent`)
extendiendo `DomainEvent` cuando el caso de uso lo justifique — no es
necesario forzarlos todos a los 3 genéricos.

Ningún servicio existente (`AuthService`, `SucursalService`,
`JoyaService`) publica eventos todavía. Conectarlos es una decisión
explícita por servicio, a tomar cuando exista al menos un consumidor
real (ver `EventBus` en `app/infrastructure/events/event_bus.py`) —
publicar eventos que nadie escucha añade código sin beneficio
verificable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """Base de todos los eventos de dominio."""

    evento_id: str = field(default_factory=lambda: str(uuid4()))
    ocurrido_en: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    entidad_tipo: str
    entidad_id: str
    usuario_id: str | None = None

    @property
    def tipo(self) -> str:
        return type(self).__name__


@dataclass(frozen=True, kw_only=True)
class EntidadCreadaEvent(DomainEvent):
    datos: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class EntidadActualizadaEvent(DomainEvent):
    campos_modificados: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class EntidadDesactivadaEvent(DomainEvent):
    motivo: str | None = None
