"""
EventBus — infraestructura de publicación/suscripción de Domain Events.

`EventBus` es el puerto (interfaz); `InMemoryEventBus` es la única
implementación de esta etapa (proceso único, sin persistencia ni
entrega garantizada — suficiente para consumidores in-process como
logging o invalidación de caché local). Si en una etapa futura se
necesita entrega garantizada entre procesos/servicios, se implementará
un adaptador nuevo (ej. `RedisEventBus`, `PostgresOutboxEventBus`) que
cumpla el mismo puerto `EventBus`, sin tocar el código que publica o
se suscribe a eventos — el mismo patrón de Repository Pattern ya usado
en todo el proyecto (`UsuarioRepository`, `SucursalRepository`, etc.).

Sin consumidores registrados en esta etapa, por mandato explícito del
Prompt Maestro de la Etapa 7.5 ("no implementar consumidores, solo
infraestructura").
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Callable

from app.domain.shared.events import DomainEvent

ManejadorEvento = Callable[[DomainEvent], None]


class EventBus(ABC):
    @abstractmethod
    def publicar(self, evento: DomainEvent) -> None: ...

    @abstractmethod
    def suscribir(self, tipo_evento: type[DomainEvent], manejador: ManejadorEvento) -> None: ...


class InMemoryEventBus(EventBus):
    def __init__(self) -> None:
        self._manejadores: dict[type[DomainEvent], list[ManejadorEvento]] = defaultdict(list)

    def publicar(self, evento: DomainEvent) -> None:
        for tipo_evento, manejadores in self._manejadores.items():
            if isinstance(evento, tipo_evento):
                for manejador in manejadores:
                    manejador(evento)

    def suscribir(self, tipo_evento: type[DomainEvent], manejador: ManejadorEvento) -> None:
        self._manejadores[tipo_evento].append(manejador)

    def cantidad_suscriptores(self, tipo_evento: type[DomainEvent]) -> int:
        """Utilidad para pruebas/diagnóstico."""
        return len(self._manejadores.get(tipo_evento, []))
