"""Pruebas de Domain Events y EventBus (Etapa 7.5)."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.domain.shared.events import (
    DomainEvent,
    EntidadActualizadaEvent,
    EntidadCreadaEvent,
    EntidadDesactivadaEvent,
)
from app.infrastructure.events.event_bus import InMemoryEventBus


def test_domain_event_genera_id_y_timestamp_automaticos():
    evento = EntidadCreadaEvent(entidad_tipo="Sucursal", entidad_id="s-1")
    assert evento.evento_id
    assert evento.ocurrido_en is not None
    assert evento.tipo == "EntidadCreadaEvent"


def test_domain_event_es_inmutable():
    evento = EntidadCreadaEvent(entidad_tipo="Sucursal", entidad_id="s-1")
    with pytest.raises(FrozenInstanceError):
        evento.entidad_id = "otro-id"  # type: ignore[misc]


def test_entidad_actualizada_event_guarda_campos_modificados():
    evento = EntidadActualizadaEvent(
        entidad_tipo="Joya",
        entidad_id="j-1",
        campos_modificados={"estado": "disponible"},
    )
    assert evento.campos_modificados == {"estado": "disponible"}


def test_entidad_desactivada_event_guarda_motivo():
    evento = EntidadDesactivadaEvent(entidad_tipo="Sucursal", entidad_id="s-1", motivo="cierre")
    assert evento.motivo == "cierre"


def test_event_bus_publica_solo_a_suscriptores_del_tipo_correcto():
    bus = InMemoryEventBus()
    recibidos_creacion: list[DomainEvent] = []
    recibidos_actualizacion: list[DomainEvent] = []

    bus.suscribir(EntidadCreadaEvent, recibidos_creacion.append)
    bus.suscribir(EntidadActualizadaEvent, recibidos_actualizacion.append)

    evento_creacion = EntidadCreadaEvent(entidad_tipo="Sucursal", entidad_id="s-1")
    bus.publicar(evento_creacion)

    assert recibidos_creacion == [evento_creacion]
    assert recibidos_actualizacion == []


def test_event_bus_soporta_multiples_suscriptores_del_mismo_evento():
    bus = InMemoryEventBus()
    contador = {"a": 0, "b": 0}

    bus.suscribir(EntidadCreadaEvent, lambda e: contador.__setitem__("a", contador["a"] + 1))
    bus.suscribir(EntidadCreadaEvent, lambda e: contador.__setitem__("b", contador["b"] + 1))

    bus.publicar(EntidadCreadaEvent(entidad_tipo="Sucursal", entidad_id="s-1"))

    assert contador == {"a": 1, "b": 1}


def test_event_bus_suscriptor_a_domain_event_base_recibe_cualquier_subtipo():
    bus = InMemoryEventBus()
    recibidos: list[DomainEvent] = []
    bus.suscribir(DomainEvent, recibidos.append)

    bus.publicar(EntidadCreadaEvent(entidad_tipo="Sucursal", entidad_id="s-1"))
    bus.publicar(EntidadDesactivadaEvent(entidad_tipo="Sucursal", entidad_id="s-1"))

    assert len(recibidos) == 2


def test_event_bus_sin_suscriptores_no_lanza_error():
    bus = InMemoryEventBus()
    bus.publicar(EntidadCreadaEvent(entidad_tipo="Sucursal", entidad_id="s-1"))  # no debe fallar


def test_cantidad_suscriptores_utilidad_de_diagnostico():
    bus = InMemoryEventBus()
    assert bus.cantidad_suscriptores(EntidadCreadaEvent) == 0
    bus.suscribir(EntidadCreadaEvent, lambda e: None)
    assert bus.cantidad_suscriptores(EntidadCreadaEvent) == 1
