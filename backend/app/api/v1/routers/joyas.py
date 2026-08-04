"""
Router de joyas: /api/v1/joyas/*

Primera diferencia deliberada respecto al patrón de `sucursales`
(Etapa 6): la escritura no se restringe solo a `administrador`, sino
también a `joyero` — el rol que en la práctica gestiona el catálogo de
piezas del taller. `sucursales` sigue siendo administrador-only porque
la organización física de la empresa sí es una decisión exclusiva de
administración.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.v1.dependencies import get_current_user, require_roles
from app.api.v1.schemas.pagination import ParametrosPaginacion, RespuestaPaginada
from app.application.dto.joya_dto import (
    CambiarEstadoRequest,
    JoyaCreateRequest,
    JoyaResponse,
    JoyaUpdateRequest,
)
from app.application.services.joya_service import JoyaService
from app.dependencies import get_joya_service
from app.domain.entities.joya import EstadoJoya, TipoJoya
from app.domain.entities.user import RolUsuario

router = APIRouter(prefix="/joyas", tags=["Joyas"])

_PUEDE_ESCRIBIR = require_roles(RolUsuario.ADMINISTRADOR, RolUsuario.JOYERO)


@router.get("", response_model=RespuestaPaginada[JoyaResponse])
def listar_joyas(
    parametros: ParametrosPaginacion = Depends(),
    tipo: TipoJoya | None = None,
    estado: EstadoJoya | None = None,
    sucursal_id: str | None = None,
    esmeralda_id: str | None = None,
    servicio: JoyaService = Depends(get_joya_service),
    _usuario=Depends(get_current_user),
) -> RespuestaPaginada[JoyaResponse]:
    items, total = servicio.listar(
        offset=parametros.offset,
        limit=parametros.limit,
        tipo=tipo,
        estado=estado,
        sucursal_id=sucursal_id,
        esmeralda_id=esmeralda_id,
    )
    return RespuestaPaginada.construir(items, total, parametros)


@router.get("/{joya_id}", response_model=JoyaResponse)
def obtener_joya(
    joya_id: str,
    servicio: JoyaService = Depends(get_joya_service),
    _usuario=Depends(get_current_user),
) -> JoyaResponse:
    return servicio.obtener(joya_id)


@router.post("", response_model=JoyaResponse, status_code=status.HTTP_201_CREATED)
def crear_joya(
    datos: JoyaCreateRequest,
    servicio: JoyaService = Depends(get_joya_service),
    _usuario=Depends(_PUEDE_ESCRIBIR),
) -> JoyaResponse:
    return servicio.crear(datos)


@router.put("/{joya_id}", response_model=JoyaResponse)
def actualizar_joya(
    joya_id: str,
    datos: JoyaUpdateRequest,
    servicio: JoyaService = Depends(get_joya_service),
    _usuario=Depends(_PUEDE_ESCRIBIR),
) -> JoyaResponse:
    return servicio.actualizar(joya_id, datos)


@router.patch("/{joya_id}/estado", response_model=JoyaResponse)
def cambiar_estado_joya(
    joya_id: str,
    datos: CambiarEstadoRequest,
    servicio: JoyaService = Depends(get_joya_service),
    _usuario=Depends(_PUEDE_ESCRIBIR),
) -> JoyaResponse:
    """Cambia el estado de la joya siguiendo la máquina de estados del
    dominio (ver `app/domain/entities/joya.py`). No permite establecer
    'vendida' directamente — ver docstring del servicio."""
    return servicio.cambiar_estado(joya_id, datos.nuevo_estado)
