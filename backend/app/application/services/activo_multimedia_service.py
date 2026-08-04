"""
Servicio de aplicación: activos multimedia (Etapa 10).

Valida que la entidad relacionada (`entidad_tipo`/`entidad_id`) exista
cuando el tipo es uno de los conocidos (Joya, Esmeralda, Certificado);
tipos de entidad futuros que aún no tengan un validador registrado se
aceptan sin validar existencia (extensible sin modificar esta clase
cada vez que aparezca una entidad nueva — ver `registrar_validador`).
"""

from __future__ import annotations

from collections.abc import Callable

from app.application.dto.activo_multimedia_dto import (
    ActivoMultimediaCreateRequest,
    ActivoMultimediaResponse,
)
from app.application.errors import EntidadNoEncontradaError
from app.domain.entities.activo_multimedia import ActivoMultimedia, TipoActivoMultimedia
from app.domain.repositories.activo_multimedia_repository import ActivoMultimediaRepository
from app.domain.shared.events import EntidadCreadaEvent, EntidadDesactivadaEvent
from app.infrastructure.events.event_bus import EventBus
from app.infrastructure.events.version_registry import RegistradorVersion
from app.infrastructure.logging.structured_logger import get_logger

logger = get_logger("activo_multimedia_service")

ValidadorExistencia = Callable[[str], bool]


class ActivoMultimediaService:
    def __init__(
        self,
        repositorio: ActivoMultimediaRepository,
        event_bus: EventBus,
        registrador_version: RegistradorVersion,
        validadores_entidad: dict[str, ValidadorExistencia] | None = None,
    ) -> None:
        self._repo = repositorio
        self._event_bus = event_bus
        self._registrador_version = registrador_version
        self._validadores: dict[str, ValidadorExistencia] = validadores_entidad or {}

    def registrar_validador(self, entidad_tipo: str, validador: ValidadorExistencia) -> None:
        """Permite registrar, sin modificar esta clase, un validador de
        existencia para un `entidad_tipo` nuevo (ej. cuando la Etapa 13
        active capturas de IA: `registrar_validador("Esmeralda", ...)`)."""
        self._validadores[entidad_tipo] = validador

    def crear(self, datos: ActivoMultimediaCreateRequest, usuario_id: str | None) -> ActivoMultimediaResponse:
        validador = self._validadores.get(datos.entidad_tipo)
        if validador is not None and not validador(datos.entidad_id):
            raise EntidadNoEncontradaError(
                f"{datos.entidad_tipo} {datos.entidad_id} no encontrada — no se puede "
                "asociar el activo multimedia"
            )

        activo = ActivoMultimedia(
            entidad_tipo=datos.entidad_tipo,
            entidad_id=datos.entidad_id,
            tipo=datos.tipo,
            url=datos.url,
            hash_sha256=datos.hash_sha256,
            dispositivo=datos.dispositivo,
        )
        activo = self._repo.crear(activo, usuario_id)

        logger.info(
            "Activo multimedia creado",
            extra={
                "activo_id": activo.id,
                "entidad_tipo": activo.entidad_tipo,
                "entidad_id": activo.entidad_id,
                "tipo": activo.tipo.value,
                "usuario_id": usuario_id,
            },
        )
        self._event_bus.publicar(
            EntidadCreadaEvent(
                entidad_tipo="ActivoMultimedia",
                entidad_id=activo.id,
                usuario_id=usuario_id,
                datos={
                    "entidad_relacionada_tipo": activo.entidad_tipo,
                    "entidad_relacionada_id": activo.entidad_id,
                    "tipo": activo.tipo.value,
                    "hash_sha256": activo.hash_sha256,
                },
            )
        )
        self._registrador_version.registrar_version(
            entidad_tipo="ActivoMultimedia",
            entidad_id=activo.id,
            version=activo.version,
            usuario_id=usuario_id,
            motivo=f"Registro de {activo.tipo.value} para {activo.entidad_tipo} {activo.entidad_id}",
        )
        return self._a_response(activo)

    def obtener(self, activo_id: str) -> ActivoMultimediaResponse:
        activo = self._obtener_o_lanzar(activo_id)
        return self._a_response(activo)

    def desactivar(self, activo_id: str, usuario_id: str | None) -> ActivoMultimediaResponse:
        self._obtener_o_lanzar(activo_id)
        activo = self._repo.desactivar(activo_id, usuario_id)

        logger.info("Activo multimedia desactivado", extra={"activo_id": activo_id, "usuario_id": usuario_id})
        self._event_bus.publicar(
            EntidadDesactivadaEvent(
                entidad_tipo="ActivoMultimedia",
                entidad_id=activo_id,
                usuario_id=usuario_id,
                motivo="Baja lógica solicitada",
            )
        )
        self._registrador_version.registrar_version(
            entidad_tipo="ActivoMultimedia",
            entidad_id=activo_id,
            version=activo.version,
            usuario_id=usuario_id,
            motivo="Desactivación",
        )
        return self._a_response(activo)

    def listar(
        self,
        offset: int,
        limit: int,
        entidad_tipo: str | None,
        entidad_id: str | None,
        tipo: TipoActivoMultimedia | None,
    ) -> tuple[list[ActivoMultimediaResponse], int]:
        items, total = self._repo.listar(offset, limit, entidad_tipo, entidad_id, tipo)
        return [self._a_response(i) for i in items], total

    def _obtener_o_lanzar(self, activo_id: str) -> ActivoMultimedia:
        activo = self._repo.obtener_por_id(activo_id)
        if activo is None:
            raise EntidadNoEncontradaError(f"Activo multimedia {activo_id} no encontrado")
        return activo

    @staticmethod
    def _a_response(activo: ActivoMultimedia) -> ActivoMultimediaResponse:
        return ActivoMultimediaResponse(
            id=activo.id,
            entidad_tipo=activo.entidad_tipo,
            entidad_id=activo.entidad_id,
            tipo=activo.tipo,
            url=activo.url,
            hash_sha256=activo.hash_sha256,
            dispositivo=activo.dispositivo,
            version=activo.version,
            creado_en=activo.creado_en,
            actualizado_en=activo.actualizado_en,
            creado_por=activo.creado_por,
            actualizado_por=activo.actualizado_por,
        )
