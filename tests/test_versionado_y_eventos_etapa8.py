"""Pruebas de infraestructura nueva de la Etapa 8: CamposVersion y el
consumidor de logging de auditoría de Domain Events."""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.shared.auditoria import CamposAuditoria
from app.domain.shared.events import EntidadCreadaEvent
from app.domain.shared.versionado import CamposVersion
from app.infrastructure.events.consumers import suscribir_logging_auditoria
from app.infrastructure.events.event_bus import InMemoryEventBus


def test_campos_version_por_defecto_es_1():
    @dataclass(kw_only=True)
    class _Entidad(CamposVersion):
        nombre: str

    entidad = _Entidad(nombre="prueba")
    assert entidad.version == 1


def test_campos_version_se_combina_con_campos_auditoria():
    @dataclass(kw_only=True)
    class _Entidad(CamposAuditoria, CamposVersion):
        nombre: str

    entidad = _Entidad(nombre="prueba")
    assert entidad.version == 1
    assert entidad.creado_en is None
    assert entidad.esta_eliminado is False


def test_suscribir_logging_auditoria_registra_un_suscriptor():
    bus = InMemoryEventBus()
    from app.domain.shared.events import DomainEvent

    assert bus.cantidad_suscriptores(DomainEvent) == 0
    suscribir_logging_auditoria(bus)
    assert bus.cantidad_suscriptores(DomainEvent) == 1


def test_consumidor_de_auditoria_no_lanza_error_al_recibir_evento(caplog):
    bus = InMemoryEventBus()
    suscribir_logging_auditoria(bus)

    evento = EntidadCreadaEvent(
        entidad_tipo="Esmeralda", entidad_id="esm-1", usuario_id="user-1", datos={"x": 1}
    )
    bus.publicar(evento)  # no debe lanzar excepción


def test_consumidor_de_auditoria_captura_subtipos_de_domain_event():
    from app.domain.shared.events import EntidadActualizadaEvent, EntidadDesactivadaEvent

    bus = InMemoryEventBus()
    recibidos = []

    # Verificamos indirectamente: nos suscribimos igual que lo hace
    # suscribir_logging_auditoria (a la clase base) y confirmamos que
    # todos los subtipos activan el manejador.
    from app.domain.shared.events import DomainEvent

    bus.suscribir(DomainEvent, recibidos.append)

    bus.publicar(EntidadCreadaEvent(entidad_tipo="Esmeralda", entidad_id="e-1"))
    bus.publicar(EntidadActualizadaEvent(entidad_tipo="Esmeralda", entidad_id="e-1"))
    bus.publicar(EntidadDesactivadaEvent(entidad_tipo="Esmeralda", entidad_id="e-1"))

    assert len(recibidos) == 3
