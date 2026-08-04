"""
Router de inventario: /api/v1/inventario/*

Sin `PUT` que sobrescriba `cantidad` directamente (ADR-009-01): existen
dos operaciones de escritura separadas — `PUT .../mover` (cambia
sucursal/ubicación) y `PATCH .../ajustar` (cambia `cantidad` por
delta, con `motivo` obligatorio).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.v1.dependencies import get_current_user, require_roles
from app.api.v1.schemas.pagination import ParametrosPaginacion, RespuestaPaginada
from app.application.dto.inventario_dto import (
    InventarioAjustarCantidadRequest,
    InventarioCreateRequest,
    InventarioMoverRequest,
    InventarioResponse,
)
from app.application.services.inventario_service import InventarioService
from app.dependencies import get_inventario_service
from app.domain.entities.user import RolUsuario, Usuario

router = APIRouter(prefix="/inventario", tags=["Inventario"])

_PUEDE_ESCRIBIR = require_roles(RolUsuario.ADMINISTRADOR, RolUsuario.JOYERO)


@router.get("", response_model=RespuestaPaginada[InventarioResponse])
def listar_inventario(
    parametros: ParametrosPaginacion = Depends(),
    sucursal_id: str | None = None,
    joya_id: str | None = None,
    cantidad_min: int | None = None,
    servicio: InventarioService = Depends(get_inventario_service),
    _usuario=Depends(get_current_user),
) -> RespuestaPaginada[InventarioResponse]:
    items, total = servicio.listar(
        offset=parametros.offset,
        limit=parametros.limit,
        sucursal_id=sucursal_id,
        joya_id=joya_id,
        cantidad_min=cantidad_min,
    )
    return RespuestaPaginada.construir(items, total, parametros)


@router.get("/{inventario_id}", response_model=InventarioResponse)
def obtener_inventario(
    inventario_id: str,
    servicio: InventarioService = Depends(get_inventario_service),
    _usuario=Depends(get_current_user),
) -> InventarioResponse:
    return servicio.obtener(inventario_id)


@router.get("/joya/{joya_id}", response_model=InventarioResponse)
def obtener_inventario_por_joya(
    joya_id: str,
    servicio: InventarioService = Depends(get_inventario_service),
    _usuario=Depends(get_current_user),
) -> InventarioResponse:
    return servicio.obtener_por_joya(joya_id)


@router.post("", response_model=InventarioResponse, status_code=status.HTTP_201_CREATED)
def crear_inventario(
    datos: InventarioCreateRequest,
    servicio: InventarioService = Depends(get_inventario_service),
    usuario: Usuario = Depends(_PUEDE_ESCRIBIR),
) -> InventarioResponse:
    return servicio.crear(datos, usuario_id=usuario.id)


@router.put("/{inventario_id}/mover", response_model=InventarioResponse)
def mover_inventario(
    inventario_id: str,
    datos: InventarioMoverRequest,
    servicio: InventarioService = Depends(get_inventario_service),
    usuario: Usuario = Depends(_PUEDE_ESCRIBIR),
) -> InventarioResponse:
    """Cambia sucursal/ubicación física. `version` debe coincidir con
    la versión actual (Optimistic Locking)."""
    return servicio.mover(inventario_id, datos, usuario_id=usuario.id)


@router.patch("/{inventario_id}/ajustar", response_model=InventarioResponse)
def ajustar_cantidad_inventario(
    inventario_id: str,
    datos: InventarioAjustarCantidadRequest,
    servicio: InventarioService = Depends(get_inventario_service),
    usuario: Usuario = Depends(_PUEDE_ESCRIBIR),
) -> InventarioResponse:
    """Ajusta `cantidad` por `delta` (ADR-009-01). `motivo` obligatorio.
    Devuelve 422 si el resultado sería negativo o si `version` no
    coincide con la versión actual."""
    return servicio.ajustar_cantidad(inventario_id, datos, usuario_id=usuario.id)
