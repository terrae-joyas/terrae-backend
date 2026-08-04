"""Servicio de aplicación: sucursales.

Primer servicio construido con las excepciones genéricas de
`app/application/errors.py` (Etapa 6) — patrón de referencia para los
servicios de dominio de las etapas 7 en adelante.
"""

from __future__ import annotations

from app.application.dto.sucursal_dto import (
    SucursalCreateRequest,
    SucursalResponse,
    SucursalUpdateRequest,
)
from app.application.errors import EntidadNoEncontradaError
from app.domain.entities.sucursal import Sucursal, TipoSucursal
from app.domain.repositories.sucursal_repository import SucursalRepository


class SucursalService:
    def __init__(self, repositorio: SucursalRepository) -> None:
        self._repo = repositorio

    def crear(self, datos: SucursalCreateRequest) -> SucursalResponse:
        sucursal = Sucursal(
            nombre=datos.nombre,
            tipo=datos.tipo,
            ciudad=datos.ciudad,
            direccion=datos.direccion,
        )
        self._repo.crear(sucursal)
        return self._a_response(sucursal)

    def obtener(self, sucursal_id: str) -> SucursalResponse:
        sucursal = self._repo.obtener_por_id(sucursal_id)
        if sucursal is None:
            raise EntidadNoEncontradaError(f"Sucursal {sucursal_id} no encontrada")
        return self._a_response(sucursal)

    def actualizar(self, sucursal_id: str, datos: SucursalUpdateRequest) -> SucursalResponse:
        sucursal = self._repo.obtener_por_id(sucursal_id)
        if sucursal is None:
            raise EntidadNoEncontradaError(f"Sucursal {sucursal_id} no encontrada")

        sucursal.nombre = datos.nombre
        sucursal.tipo = datos.tipo
        sucursal.ciudad = datos.ciudad
        sucursal.direccion = datos.direccion
        sucursal.activa = datos.activa
        self._repo.actualizar(sucursal)
        return self._a_response(sucursal)

    def desactivar(self, sucursal_id: str) -> SucursalResponse:
        """Baja lógica (nunca se elimina físicamente un registro con
        historial potencial de joyas/ventas/inventario asociado)."""
        sucursal = self._repo.obtener_por_id(sucursal_id)
        if sucursal is None:
            raise EntidadNoEncontradaError(f"Sucursal {sucursal_id} no encontrada")
        sucursal.activa = False
        self._repo.actualizar(sucursal)
        return self._a_response(sucursal)

    def listar(
        self,
        offset: int,
        limit: int,
        tipo: TipoSucursal | None,
        ciudad: str | None,
        activa: bool | None,
    ) -> tuple[list[SucursalResponse], int]:
        sucursales, total = self._repo.listar(offset, limit, tipo, ciudad, activa)
        return [self._a_response(s) for s in sucursales], total

    @staticmethod
    def _a_response(sucursal: Sucursal) -> SucursalResponse:
        return SucursalResponse(
            id=sucursal.id,
            nombre=sucursal.nombre,
            tipo=sucursal.tipo,
            ciudad=sucursal.ciudad,
            direccion=sucursal.direccion,
            activa=sucursal.activa,
            creado_en=sucursal.creado_en,
        )
