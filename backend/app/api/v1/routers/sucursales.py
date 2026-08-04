"""
Router de sucursales: /api/v1/sucursales/*

Patrón de referencia (Etapa 6) para los routers de dominio de las
etapas 7 en adelante:
- Listado paginado + filtrado vía `ParametrosPaginacion` / `RespuestaPaginada`.
- Lectura pública (cualquier usuario autenticado); escritura restringida
  a `administrador`.
- Sin `try/except`: las excepciones de `app.application.errors` las
  traduce `app/api/v1/error_handlers.py` de forma centralizada.
- Baja lógica (`activa=False`), nunca DELETE físico — una sucursal
  puede tener joyas/inventario/ventas asociadas (Etapa 5).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.v1.dependencies import get_current_user, require_roles
from app.api.v1.schemas.pagination import ParametrosPaginacion, RespuestaPaginada
from app.application.dto.sucursal_dto import (
    SucursalCreateRequest,
    SucursalResponse,
    SucursalUpdateRequest,
)
from app.application.services.sucursal_service import SucursalService
from app.dependencies import get_sucursal_service
from app.domain.entities.sucursal import TipoSucursal
from app.domain.entities.user import RolUsuario

router = APIRouter(prefix="/sucursales", tags=["Sucursales"])


@router.get("", response_model=RespuestaPaginada[SucursalResponse])
def listar_sucursales(
    parametros: ParametrosPaginacion = Depends(),
    tipo: TipoSucursal | None = None,
    ciudad: str | None = None,
    activa: bool | None = None,
    servicio: SucursalService = Depends(get_sucursal_service),
    _usuario=Depends(get_current_user),
) -> RespuestaPaginada[SucursalResponse]:
    items, total = servicio.listar(
        offset=parametros.offset,
        limit=parametros.limit,
        tipo=tipo,
        ciudad=ciudad,
        activa=activa,
    )
    return RespuestaPaginada.construir(items, total, parametros)


@router.get("/{sucursal_id}", response_model=SucursalResponse)
def obtener_sucursal(
    sucursal_id: str,
    servicio: SucursalService = Depends(get_sucursal_service),
    _usuario=Depends(get_current_user),
) -> SucursalResponse:
    return servicio.obtener(sucursal_id)


@router.post("", response_model=SucursalResponse, status_code=status.HTTP_201_CREATED)
def crear_sucursal(
    datos: SucursalCreateRequest,
    servicio: SucursalService = Depends(get_sucursal_service),
    _usuario=Depends(require_roles(RolUsuario.ADMINISTRADOR)),
) -> SucursalResponse:
    return servicio.crear(datos)


@router.put("/{sucursal_id}", response_model=SucursalResponse)
def actualizar_sucursal(
    sucursal_id: str,
    datos: SucursalUpdateRequest,
    servicio: SucursalService = Depends(get_sucursal_service),
    _usuario=Depends(require_roles(RolUsuario.ADMINISTRADOR)),
) -> SucursalResponse:
    return servicio.actualizar(sucursal_id, datos)


@router.delete("/{sucursal_id}", response_model=SucursalResponse)
def desactivar_sucursal(
    sucursal_id: str,
    servicio: SucursalService = Depends(get_sucursal_service),
    _usuario=Depends(require_roles(RolUsuario.ADMINISTRADOR)),
) -> SucursalResponse:
    """Baja lógica — ver docstring del módulo."""
    return servicio.desactivar(sucursal_id)
