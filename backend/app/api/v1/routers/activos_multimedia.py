"""
Router de activos multimedia: /api/v1/activos-multimedia/*

Entidad polimórfica transversal (ADR-010-01): cualquier archivo
multimedia trazable (foto de joya, imagen microscópica, certificado
escaneado, recurso visual) se registra aquí, asociado a su entidad de
negocio vía `entidad_tipo`/`entidad_id`.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.v1.dependencies import get_current_user, require_roles
from app.api.v1.schemas.pagination import ParametrosPaginacion, RespuestaPaginada
from app.application.dto.activo_multimedia_dto import (
    ActivoMultimediaCreateRequest,
    ActivoMultimediaResponse,
)
from app.application.services.activo_multimedia_service import ActivoMultimediaService
from app.dependencies import get_activo_multimedia_service
from app.domain.entities.activo_multimedia import TipoActivoMultimedia
from app.domain.entities.user import RolUsuario, Usuario

router = APIRouter(prefix="/activos-multimedia", tags=["Activos Multimedia"])

_PUEDE_ESCRIBIR = require_roles(RolUsuario.ADMINISTRADOR, RolUsuario.JOYERO)


@router.get("", response_model=RespuestaPaginada[ActivoMultimediaResponse])
def listar_activos_multimedia(
    parametros: ParametrosPaginacion = Depends(),
    entidad_tipo: str | None = None,
    entidad_id: str | None = None,
    tipo: TipoActivoMultimedia | None = None,
    servicio: ActivoMultimediaService = Depends(get_activo_multimedia_service),
    _usuario=Depends(get_current_user),
) -> RespuestaPaginada[ActivoMultimediaResponse]:
    items, total = servicio.listar(parametros.offset, parametros.limit, entidad_tipo, entidad_id, tipo)
    return RespuestaPaginada.construir(items, total, parametros)


@router.get("/{activo_id}", response_model=ActivoMultimediaResponse)
def obtener_activo_multimedia(
    activo_id: str,
    servicio: ActivoMultimediaService = Depends(get_activo_multimedia_service),
    _usuario=Depends(get_current_user),
) -> ActivoMultimediaResponse:
    return servicio.obtener(activo_id)


@router.post("", response_model=ActivoMultimediaResponse, status_code=status.HTTP_201_CREATED)
def crear_activo_multimedia(
    datos: ActivoMultimediaCreateRequest,
    servicio: ActivoMultimediaService = Depends(get_activo_multimedia_service),
    usuario: Usuario = Depends(_PUEDE_ESCRIBIR),
) -> ActivoMultimediaResponse:
    """Registra un activo multimedia ya alojado externamente (`url`) con
    su hash de integridad. El pipeline de subida real de archivos es
    objeto de la Etapa 14; esta etapa establece el contrato de
    metadatos y trazabilidad (autor, fecha, dispositivo, versión, hash,
    relación) exigido explícitamente para todo archivo multimedia."""
    return servicio.crear(datos, usuario_id=usuario.id)


@router.delete("/{activo_id}", response_model=ActivoMultimediaResponse)
def desactivar_activo_multimedia(
    activo_id: str,
    servicio: ActivoMultimediaService = Depends(get_activo_multimedia_service),
    usuario: Usuario = Depends(_PUEDE_ESCRIBIR),
) -> ActivoMultimediaResponse:
    """Baja lógica — un activo multimedia nunca se borra físicamente."""
    return servicio.desactivar(activo_id, usuario_id=usuario.id)
