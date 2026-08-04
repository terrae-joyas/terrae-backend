"""
Consumidores de Domain Events (Etapa 8 — ADR-008-03).

`suscribir_logging_auditoria` es el consumidor de referencia: genérico,
reutilizable por cualquier entidad futura que publique eventos, sin
necesitar registrar nada propio. Se conecta una única vez al arrancar
la aplicación (ver `app/main.py::configurar_event_bus`).
"""

from __future__ import annotations

from app.domain.shared.events import DomainEvent
from app.infrastructure.events.event_bus import EventBus
from app.infrastructure.logging.structured_logger import get_logger

logger = get_logger("domain_events")


def _registrar_evento_en_log(evento: DomainEvent) -> None:
    logger.info(
        f"Domain event: {evento.tipo}",
        extra={
            "evento_id": evento.evento_id,
            "evento_tipo": evento.tipo,
            "entidad_tipo": evento.entidad_tipo,
            "entidad_id": evento.entidad_id,
            "usuario_id": evento.usuario_id,
            "ocurrido_en": evento.ocurrido_en.isoformat(),
        },
    )


def suscribir_logging_auditoria(event_bus: EventBus) -> None:
    """Suscribe el consumidor de auditoría a TODOS los Domain Events
    (se suscribe a la clase base `DomainEvent`, capturando cualquier
    subtipo presente y futuro sin necesitar suscripciones adicionales)."""
    event_bus.suscribir(DomainEvent, _registrar_evento_en_log)
