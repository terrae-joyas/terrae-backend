"""Servicio de aplicación: joyas.

Reglas de negocio implementadas en esta etapa:
1. Si se indica `esmeralda_id`, debe existir.
2. Una esmeralda no puede estar vinculada a más de una joya activa
   (cualquier estado distinto de `dada_de_baja`) a la vez.
3. Si se indica `sucursal_id`, debe existir.
4. La `referencia` es única (se valida antes de insertar, además de la
   restricción `UNIQUE` de la base de datos como última línea de defensa).
5. Los cambios de estado solo pueden seguir transiciones válidas
   (`Joya.puede_transicionar_a`); nunca se puede establecer `VENDIDA`
   desde este servicio — eso lo hace el módulo de Ventas (Etapa 19).
"""

from __future__ import annotations

from app.application.dto.joya_dto import (
    JoyaCreateRequest,
    JoyaResponse,
    JoyaUpdateRequest,
)
from app.application.errors import (
    EntidadDuplicadaError,
    EntidadNoEncontradaError,
    OperacionNoPermitidaError,
)
from app.domain.entities.joya import EstadoJoya, Joya, TipoJoya
from app.domain.repositories.esmeralda_repository import EsmeraldaRepository
from app.domain.repositories.joya_repository import JoyaRepository
from app.domain.repositories.sucursal_repository import SucursalRepository


class JoyaService:
    def __init__(
        self,
        repositorio: JoyaRepository,
        esmeralda_repositorio: EsmeraldaRepository,
        sucursal_repositorio: SucursalRepository,
    ) -> None:
        self._repo = repositorio
        self._esmeraldas = esmeralda_repositorio
        self._sucursales = sucursal_repositorio

    def crear(self, datos: JoyaCreateRequest) -> JoyaResponse:
        if self._repo.obtener_por_referencia(datos.referencia):
            raise EntidadDuplicadaError(f"La referencia '{datos.referencia}' ya está en uso")

        self._validar_esmeralda(datos.esmeralda_id)
        self._validar_sucursal(datos.sucursal_id)

        joya = Joya(
            referencia=datos.referencia,
            nombre=datos.nombre,
            tipo=datos.tipo,
            material_metal=datos.material_metal,
            esmeralda_id=datos.esmeralda_id,
            sucursal_id=datos.sucursal_id,
        )
        self._repo.crear(joya)
        return self._a_response(joya)

    def obtener(self, joya_id: str) -> JoyaResponse:
        joya = self._obtener_o_lanzar(joya_id)
        return self._a_response(joya)

    def actualizar(self, joya_id: str, datos: JoyaUpdateRequest) -> JoyaResponse:
        joya = self._obtener_o_lanzar(joya_id)

        if datos.esmeralda_id != joya.esmeralda_id:
            self._validar_esmeralda(datos.esmeralda_id, excluir_joya_id=joya.id)
        if datos.sucursal_id != joya.sucursal_id:
            self._validar_sucursal(datos.sucursal_id)

        joya.nombre = datos.nombre
        joya.tipo = datos.tipo
        joya.material_metal = datos.material_metal
        joya.esmeralda_id = datos.esmeralda_id
        joya.sucursal_id = datos.sucursal_id
        self._repo.actualizar(joya)
        return self._a_response(joya)

    def cambiar_estado(self, joya_id: str, nuevo_estado: EstadoJoya) -> JoyaResponse:
        joya = self._obtener_o_lanzar(joya_id)

        if nuevo_estado == EstadoJoya.VENDIDA:
            raise OperacionNoPermitidaError(
                "No se puede marcar una joya como 'vendida' directamente. "
                "Ese estado se asigna automáticamente al registrar una venta "
                "(módulo de Ventas, Etapa 19)."
            )
        if not joya.puede_transicionar_a(nuevo_estado):
            raise OperacionNoPermitidaError(
                f"Transición inválida: '{joya.estado.value}' → '{nuevo_estado.value}'"
            )

        joya.estado = nuevo_estado
        self._repo.actualizar(joya)
        return self._a_response(joya)

    def listar(
        self,
        offset: int,
        limit: int,
        tipo: TipoJoya | None,
        estado: EstadoJoya | None,
        sucursal_id: str | None,
        esmeralda_id: str | None,
    ) -> tuple[list[JoyaResponse], int]:
        joyas, total = self._repo.listar(offset, limit, tipo, estado, sucursal_id, esmeralda_id)
        return [self._a_response(j) for j in joyas], total

    # --- Helpers internos ---
    def _obtener_o_lanzar(self, joya_id: str) -> Joya:
        joya = self._repo.obtener_por_id(joya_id)
        if joya is None:
            raise EntidadNoEncontradaError(f"Joya {joya_id} no encontrada")
        return joya

    def _validar_esmeralda(self, esmeralda_id: str | None, excluir_joya_id: str | None = None) -> None:
        if esmeralda_id is None:
            return
        if self._esmeraldas.obtener_por_id(esmeralda_id) is None:
            raise EntidadNoEncontradaError(f"Esmeralda {esmeralda_id} no encontrada")
        if self._esmeraldas.esta_vinculada_a_joya_activa(esmeralda_id, excluir_joya_id):
            raise EntidadDuplicadaError(
                f"La esmeralda {esmeralda_id} ya está vinculada a otra joya activa"
            )

    def _validar_sucursal(self, sucursal_id: str | None) -> None:
        if sucursal_id is None:
            return
        if self._sucursales.obtener_por_id(sucursal_id) is None:
            raise EntidadNoEncontradaError(f"Sucursal {sucursal_id} no encontrada")

    @staticmethod
    def _a_response(joya: Joya) -> JoyaResponse:
        return JoyaResponse(
            id=joya.id,
            referencia=joya.referencia,
            nombre=joya.nombre,
            tipo=joya.tipo,
            material_metal=joya.material_metal,
            estado=joya.estado,
            esmeralda_id=joya.esmeralda_id,
            sucursal_id=joya.sucursal_id,
            creado_en=joya.creado_en,
        )
