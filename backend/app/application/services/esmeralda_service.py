"""
Servicio de aplicación: esmeraldas (Etapa 8).

Primera entidad del proyecto que implementa el régimen completo de
`CONSTITUCION_INGENIERIA_TERRAE.md` §4: auditoría, versionado, Domain
Events, logging y Optimistic Locking.

Reglas de negocio:
1. `codigo_interno` único.
2. Optimistic Locking obligatorio en `actualizar` (ADR-008-04).
3. Toda creación/actualización/desactivación publica un Domain Event
   (ADR-008-01) y queda registrada en el historial de versiones
   (ADR-008-02, reutilizando `historial_eventos` de la Etapa 5).
"""

from __future__ import annotations

from app.application.dto.esmeralda_dto import (
    EsmeraldaCreateRequest,
    EsmeraldaResponse,
    EsmeraldaUpdateRequest,
)
from app.application.errors import EntidadDuplicadaError, EntidadNoEncontradaError
from app.domain.entities.esmeralda import Esmeralda, MinaOrigen
from app.domain.repositories.esmeralda_repository import EsmeraldaRepository
from app.domain.shared.events import (
    EntidadActualizadaEvent,
    EntidadCreadaEvent,
    EntidadDesactivadaEvent,
)
from app.infrastructure.events.event_bus import EventBus
from app.infrastructure.events.version_registry import RegistradorVersion
from app.infrastructure.logging.structured_logger import get_logger

logger = get_logger("esmeralda_service")


class EsmeraldaService:
    def __init__(
        self,
        repositorio: EsmeraldaRepository,
        event_bus: EventBus,
        registrador_version: RegistradorVersion,
    ) -> None:
        self._repo = repositorio
        self._event_bus = event_bus
        self._registrador_version = registrador_version

    def crear(self, datos: EsmeraldaCreateRequest, usuario_id: str | None) -> EsmeraldaResponse:
        if self._repo.obtener_por_codigo_interno(datos.codigo_interno):
            raise EntidadDuplicadaError(f"El código interno '{datos.codigo_interno}' ya está en uso")

        esmeralda = Esmeralda(
            codigo_interno=datos.codigo_interno,
            mina_origen=datos.mina_origen,
            quilates=datos.quilates,
            color=datos.color,
            claridad=datos.claridad,
            corte=datos.corte,
            tratamientos=datos.tratamientos,
            tipo_inclusion_principal=datos.tipo_inclusion_principal,
        )
        esmeralda = self._repo.crear(esmeralda, usuario_id)

        logger.info(
            "Esmeralda creada",
            extra={"esmeralda_id": esmeralda.id, "usuario_id": usuario_id, "mina_origen": esmeralda.mina_origen.value},
        )
        self._event_bus.publicar(
            EntidadCreadaEvent(
                entidad_tipo="Esmeralda",
                entidad_id=esmeralda.id,
                usuario_id=usuario_id,
                datos={"codigo_interno": esmeralda.codigo_interno, "mina_origen": esmeralda.mina_origen.value},
            )
        )
        self._registrador_version.registrar_version(
            entidad_tipo="Esmeralda",
            entidad_id=esmeralda.id,
            version=esmeralda.version,
            usuario_id=usuario_id,
            motivo="Creación inicial",
        )
        return self._a_response(esmeralda)

    def obtener(self, esmeralda_id: str) -> EsmeraldaResponse:
        esmeralda = self._obtener_o_lanzar(esmeralda_id)
        return self._a_response(esmeralda)

    def actualizar(
        self, esmeralda_id: str, datos: EsmeraldaUpdateRequest, usuario_id: str | None
    ) -> EsmeraldaResponse:
        esmeralda = self._obtener_o_lanzar(esmeralda_id)

        campos_modificados = {
            "mina_origen": datos.mina_origen.value,
            "quilates": datos.quilates,
            "color": datos.color,
            "claridad": datos.claridad,
            "corte": datos.corte,
            "tratamientos": datos.tratamientos,
            "tipo_inclusion_principal": datos.tipo_inclusion_principal,
        }

        esmeralda.mina_origen = datos.mina_origen
        esmeralda.quilates = datos.quilates
        esmeralda.color = datos.color
        esmeralda.claridad = datos.claridad
        esmeralda.corte = datos.corte
        esmeralda.tratamientos = datos.tratamientos
        esmeralda.tipo_inclusion_principal = datos.tipo_inclusion_principal

        # ConflictoDeVersionError se propaga desde el repositorio si
        # `datos.version` no coincide con la versión actual en BD —
        # ver ADR-008-04 (UPDATE condicional atómico).
        esmeralda_actualizada = self._repo.actualizar(esmeralda, datos.version, usuario_id)

        logger.info(
            "Esmeralda actualizada",
            extra={
                "esmeralda_id": esmeralda_id,
                "usuario_id": usuario_id,
                "version_nueva": esmeralda_actualizada.version,
            },
        )
        self._event_bus.publicar(
            EntidadActualizadaEvent(
                entidad_tipo="Esmeralda",
                entidad_id=esmeralda_id,
                usuario_id=usuario_id,
                campos_modificados=campos_modificados,
            )
        )
        self._registrador_version.registrar_version(
            entidad_tipo="Esmeralda",
            entidad_id=esmeralda_id,
            version=esmeralda_actualizada.version,
            usuario_id=usuario_id,
            motivo=datos.motivo,
        )
        return self._a_response(esmeralda_actualizada)

    def desactivar(self, esmeralda_id: str, usuario_id: str | None) -> EsmeraldaResponse:
        self._obtener_o_lanzar(esmeralda_id)
        esmeralda = self._repo.desactivar(esmeralda_id, usuario_id)

        logger.info("Esmeralda desactivada", extra={"esmeralda_id": esmeralda_id, "usuario_id": usuario_id})
        self._event_bus.publicar(
            EntidadDesactivadaEvent(
                entidad_tipo="Esmeralda",
                entidad_id=esmeralda_id,
                usuario_id=usuario_id,
                motivo="Baja lógica solicitada",
            )
        )
        self._registrador_version.registrar_version(
            entidad_tipo="Esmeralda",
            entidad_id=esmeralda_id,
            version=esmeralda.version,
            usuario_id=usuario_id,
            motivo="Desactivación",
        )
        return self._a_response(esmeralda)

    def listar(
        self,
        offset: int,
        limit: int,
        mina_origen: MinaOrigen | None,
        quilates_min: float | None,
        quilates_max: float | None,
    ) -> tuple[list[EsmeraldaResponse], int]:
        esmeraldas, total = self._repo.listar(offset, limit, mina_origen, quilates_min, quilates_max)
        return [self._a_response(e) for e in esmeraldas], total

    # --- Helpers internos ---
    def _obtener_o_lanzar(self, esmeralda_id: str) -> Esmeralda:
        esmeralda = self._repo.obtener_por_id(esmeralda_id)
        if esmeralda is None:
            raise EntidadNoEncontradaError(f"Esmeralda {esmeralda_id} no encontrada")
        return esmeralda

    @staticmethod
    def _a_response(esmeralda: Esmeralda) -> EsmeraldaResponse:
        return EsmeraldaResponse(
            id=esmeralda.id,
            codigo_interno=esmeralda.codigo_interno,
            mina_origen=esmeralda.mina_origen,
            quilates=esmeralda.quilates,
            color=esmeralda.color,
            claridad=esmeralda.claridad,
            corte=esmeralda.corte,
            tratamientos=esmeralda.tratamientos,
            tipo_inclusion_principal=esmeralda.tipo_inclusion_principal,
            version=esmeralda.version,
            creado_en=esmeralda.creado_en,
            actualizado_en=esmeralda.actualizado_en,
            creado_por=esmeralda.creado_por,
            actualizado_por=esmeralda.actualizado_por,
        )
