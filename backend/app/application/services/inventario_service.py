"""
Servicio de aplicación: inventario (Etapa 9).

Reglas de negocio:
1. La joya asociada debe existir (`JoyaRepository`).
2. Una joya no puede tener más de un registro de inventario (relación
   1:1 ya forzada por `UNIQUE(joya_id)` desde la Etapa 5).
3. La sucursal asociada debe existir (`SucursalRepository`).
4. `cantidad` nunca es negativa — ajustada exclusivamente por delta
   (ADR-009-01), nunca sobrescrita directamente.
5. Auditoría, versionado, Domain Events y logging — régimen completo
   desde la Etapa 8 (`CONSTITUCION_INGENIERIA_TERRAE.md` §4).
"""

from __future__ import annotations

from app.application.dto.inventario_dto import (
    InventarioAjustarCantidadRequest,
    InventarioCreateRequest,
    InventarioMoverRequest,
    InventarioResponse,
)
from app.application.errors import EntidadDuplicadaError, EntidadNoEncontradaError
from app.domain.entities.inventario import Inventario
from app.domain.repositories.inventario_repository import InventarioRepository
from app.domain.repositories.joya_repository import JoyaRepository
from app.domain.repositories.sucursal_repository import SucursalRepository
from app.domain.shared.events import EntidadActualizadaEvent, EntidadCreadaEvent
from app.infrastructure.events.event_bus import EventBus
from app.infrastructure.events.version_registry import RegistradorVersion
from app.infrastructure.logging.structured_logger import get_logger

logger = get_logger("inventario_service")


class InventarioService:
    def __init__(
        self,
        repositorio: InventarioRepository,
        joya_repositorio: JoyaRepository,
        sucursal_repositorio: SucursalRepository,
        event_bus: EventBus,
        registrador_version: RegistradorVersion,
    ) -> None:
        self._repo = repositorio
        self._joyas = joya_repositorio
        self._sucursales = sucursal_repositorio
        self._event_bus = event_bus
        self._registrador_version = registrador_version

    def crear(self, datos: InventarioCreateRequest, usuario_id: str | None) -> InventarioResponse:
        if self._joyas.obtener_por_id(datos.joya_id) is None:
            raise EntidadNoEncontradaError(f"Joya {datos.joya_id} no encontrada")
        if self._sucursales.obtener_por_id(datos.sucursal_id) is None:
            raise EntidadNoEncontradaError(f"Sucursal {datos.sucursal_id} no encontrada")
        if self._repo.obtener_por_joya_id(datos.joya_id) is not None:
            raise EntidadDuplicadaError(f"La joya {datos.joya_id} ya tiene un registro de inventario")

        inventario = Inventario(
            joya_id=datos.joya_id,
            sucursal_id=datos.sucursal_id,
            cantidad=datos.cantidad,
            ubicacion_fisica=datos.ubicacion_fisica,
        )
        inventario = self._repo.crear(inventario, usuario_id)

        logger.info(
            "Inventario creado",
            extra={"inventario_id": inventario.id, "joya_id": inventario.joya_id, "usuario_id": usuario_id},
        )
        self._event_bus.publicar(
            EntidadCreadaEvent(
                entidad_tipo="Inventario",
                entidad_id=inventario.id,
                usuario_id=usuario_id,
                datos={"joya_id": inventario.joya_id, "sucursal_id": inventario.sucursal_id, "cantidad": inventario.cantidad},
            )
        )
        self._registrador_version.registrar_version(
            entidad_tipo="Inventario",
            entidad_id=inventario.id,
            version=inventario.version,
            usuario_id=usuario_id,
            motivo="Creación inicial",
        )
        return self._a_response(inventario)

    def obtener(self, inventario_id: str) -> InventarioResponse:
        inventario = self._obtener_o_lanzar(inventario_id)
        return self._a_response(inventario)

    def obtener_por_joya(self, joya_id: str) -> InventarioResponse:
        inventario = self._repo.obtener_por_joya_id(joya_id)
        if inventario is None:
            raise EntidadNoEncontradaError(f"La joya {joya_id} no tiene registro de inventario")
        return self._a_response(inventario)

    def mover(
        self, inventario_id: str, datos: InventarioMoverRequest, usuario_id: str | None
    ) -> InventarioResponse:
        self._obtener_o_lanzar(inventario_id)
        if self._sucursales.obtener_por_id(datos.sucursal_id) is None:
            raise EntidadNoEncontradaError(f"Sucursal {datos.sucursal_id} no encontrada")

        actualizado = self._repo.mover(
            inventario_id, datos.sucursal_id, datos.ubicacion_fisica, datos.version, usuario_id
        )

        logger.info(
            "Inventario movido",
            extra={"inventario_id": inventario_id, "sucursal_id": datos.sucursal_id, "usuario_id": usuario_id},
        )
        self._event_bus.publicar(
            EntidadActualizadaEvent(
                entidad_tipo="Inventario",
                entidad_id=inventario_id,
                usuario_id=usuario_id,
                campos_modificados={"sucursal_id": datos.sucursal_id, "ubicacion_fisica": datos.ubicacion_fisica},
            )
        )
        self._registrador_version.registrar_version(
            entidad_tipo="Inventario",
            entidad_id=inventario_id,
            version=actualizado.version,
            usuario_id=usuario_id,
            motivo="Cambio de sucursal/ubicación",
        )
        return self._a_response(actualizado)

    def ajustar_cantidad(
        self, inventario_id: str, datos: InventarioAjustarCantidadRequest, usuario_id: str | None
    ) -> InventarioResponse:
        self._obtener_o_lanzar(inventario_id)

        # ConflictoDeVersionError / ValidacionNegocioError se propagan
        # desde el repositorio (ADR-009-01, UPDATE condicional atómico).
        actualizado = self._repo.ajustar_cantidad(inventario_id, datos.delta, datos.version, usuario_id)

        logger.info(
            "Cantidad de inventario ajustada",
            extra={
                "inventario_id": inventario_id,
                "delta": datos.delta,
                "cantidad_resultante": actualizado.cantidad,
                "motivo": datos.motivo,
                "usuario_id": usuario_id,
            },
        )
        self._event_bus.publicar(
            EntidadActualizadaEvent(
                entidad_tipo="Inventario",
                entidad_id=inventario_id,
                usuario_id=usuario_id,
                campos_modificados={"delta": datos.delta, "cantidad_resultante": actualizado.cantidad, "motivo": datos.motivo},
            )
        )
        self._registrador_version.registrar_version(
            entidad_tipo="Inventario",
            entidad_id=inventario_id,
            version=actualizado.version,
            usuario_id=usuario_id,
            motivo=datos.motivo,
        )
        return self._a_response(actualizado)

    def listar(
        self,
        offset: int,
        limit: int,
        sucursal_id: str | None,
        joya_id: str | None,
        cantidad_min: int | None,
    ) -> tuple[list[InventarioResponse], int]:
        items, total = self._repo.listar(offset, limit, sucursal_id, joya_id, cantidad_min)
        return [self._a_response(i) for i in items], total

    # --- Helpers internos ---
    def _obtener_o_lanzar(self, inventario_id: str) -> Inventario:
        inventario = self._repo.obtener_por_id(inventario_id)
        if inventario is None:
            raise EntidadNoEncontradaError(f"Inventario {inventario_id} no encontrado")
        return inventario

    @staticmethod
    def _a_response(inventario: Inventario) -> InventarioResponse:
        return InventarioResponse(
            id=inventario.id,
            joya_id=inventario.joya_id,
            sucursal_id=inventario.sucursal_id,
            cantidad=inventario.cantidad,
            ubicacion_fisica=inventario.ubicacion_fisica,
            version=inventario.version,
            creado_en=inventario.creado_en,
            actualizado_en=inventario.actualizado_en,
            creado_por=inventario.creado_por,
            actualizado_por=inventario.actualizado_por,
        )
