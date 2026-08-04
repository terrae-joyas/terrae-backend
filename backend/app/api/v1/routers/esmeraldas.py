"""
Router de esmeraldas: /api/v1/esmeraldas/*

Mismo patrón de autorización que `joyas` (administrador o joyero). El
endpoint de actualización exige `version` en el cuerpo (Optimistic
Locking, ADR-008-04): un conflicto de versión se traduce
automáticamente a HTTP 422 vía `ConflictoDeVersionError` (hereda de
`OperacionNoPermitidaError`, manejador ya registrado desde la Etapa 6).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.v1.dependencies import get_current_user, require_roles
from app.api.v1.schemas.pagination import ParametrosPaginacion, RespuestaPaginada
from app.application.dto.esmeralda_dto import (
    EsmeraldaCreateRequest,
    EsmeraldaResponse,
    EsmeraldaUpdateRequest,
)
from app.application.services.esmeralda_service import EsmeraldaService
from app.dependencies import get_esmeralda_service
from app.domain.entities.esmeralda import MinaOrigen
from app.domain.entities.user import RolUsuario, Usuario

router = APIRouter(prefix="/esmeraldas", tags=["Esmeraldas"])

_PUEDE_ESCRIBIR = require_roles(RolUsuario.ADMINISTRADOR, RolUsuario.JOYERO)


@router.get("", response_model=RespuestaPaginada[EsmeraldaResponse])
def listar_esmeraldas(
    parametros: ParametrosPaginacion = Depends(),
    mina_origen: MinaOrigen | None = None,
    quilates_min: float | None = None,
    quilates_max: float | None = None,
    servicio: EsmeraldaService = Depends(get_esmeralda_service),
    _usuario=Depends(get_current_user),
) -> RespuestaPaginada[EsmeraldaResponse]:
    items, total = servicio.listar(
        offset=parametros.offset,
        limit=parametros.limit,
        mina_origen=mina_origen,
        quilates_min=quilates_min,
        quilates_max=quilates_max,
    )
    return RespuestaPaginada.construir(items, total, parametros)


@router.get("/{esmeralda_id}", response_model=EsmeraldaResponse)
def obtener_esmeralda(
    esmeralda_id: str,
    servicio: EsmeraldaService = Depends(get_esmeralda_service),
    _usuario=Depends(get_current_user),
) -> EsmeraldaResponse:
    return servicio.obtener(esmeralda_id)


@router.post("", response_model=EsmeraldaResponse, status_code=status.HTTP_201_CREATED)
def crear_esmeralda(
    datos: EsmeraldaCreateRequest,
    servicio: EsmeraldaService = Depends(get_esmeralda_service),
    usuario: Usuario = Depends(_PUEDE_ESCRIBIR),
) -> EsmeraldaResponse:
    return servicio.crear(datos, usuario_id=usuario.id)


@router.put("/{esmeralda_id}", response_model=EsmeraldaResponse)
def actualizar_esmeralda(
    esmeralda_id: str,
    datos: EsmeraldaUpdateRequest,
    servicio: EsmeraldaService = Depends(get_esmeralda_service),
    usuario: Usuario = Depends(_PUEDE_ESCRIBIR),
) -> EsmeraldaResponse:
    """`datos.version` debe coincidir con la versión actual del
    recurso (Optimistic Locking) — de lo contrario devuelve 422."""
    return servicio.actualizar(esmeralda_id, datos, usuario_id=usuario.id)


@router.delete("/{esmeralda_id}", response_model=EsmeraldaResponse)
def desactivar_esmeralda(
    esmeralda_id: str,
    servicio: EsmeraldaService = Depends(get_esmeralda_service),
    usuario: Usuario = Depends(_PUEDE_ESCRIBIR),
) -> EsmeraldaResponse:
    """Baja lógica (`eliminado_en`/`eliminado_por`)."""
    return servicio.desactivar(esmeralda_id, usuario_id=usuario.id)
