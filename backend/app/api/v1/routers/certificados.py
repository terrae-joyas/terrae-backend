"""Router de certificados: /api/v1/certificados/*"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.v1.dependencies import get_current_user, require_roles
from app.api.v1.schemas.pagination import ParametrosPaginacion, RespuestaPaginada
from app.application.dto.certificado_dto import (
    CertificadoEmitirRequest,
    CertificadoResponse,
    CertificadoRevocarRequest,
)
from app.application.services.certificado_service import CertificadoService
from app.dependencies import get_certificado_service
from app.domain.entities.certificado import EstadoCertificado
from app.domain.entities.user import RolUsuario, Usuario

router = APIRouter(prefix="/certificados", tags=["Certificados"])

_PUEDE_ESCRIBIR = require_roles(RolUsuario.ADMINISTRADOR, RolUsuario.JOYERO)


@router.get("", response_model=RespuestaPaginada[CertificadoResponse])
def listar_certificados(
    parametros: ParametrosPaginacion = Depends(),
    joya_id: str | None = None,
    estado: EstadoCertificado | None = None,
    servicio: CertificadoService = Depends(get_certificado_service),
    _usuario=Depends(get_current_user),
) -> RespuestaPaginada[CertificadoResponse]:
    items, total = servicio.listar(parametros.offset, parametros.limit, joya_id, estado)
    return RespuestaPaginada.construir(items, total, parametros)


@router.get("/{certificado_id}", response_model=CertificadoResponse)
def obtener_certificado(
    certificado_id: str,
    servicio: CertificadoService = Depends(get_certificado_service),
    _usuario=Depends(get_current_user),
) -> CertificadoResponse:
    return servicio.obtener(certificado_id)


@router.post("", response_model=CertificadoResponse, status_code=status.HTTP_201_CREATED)
def emitir_certificado(
    datos: CertificadoEmitirRequest,
    servicio: CertificadoService = Depends(get_certificado_service),
    usuario: Usuario = Depends(_PUEDE_ESCRIBIR),
) -> CertificadoResponse:
    """Emite un certificado nuevo para la joya. `numero_certificado` y
    `hash_sha256` se generan server-side — nunca los decide el
    cliente. Devuelve 409 si la joya ya tiene un certificado vigente."""
    return servicio.emitir(datos, usuario_id=usuario.id)


@router.post("/{certificado_id}/revocar", response_model=CertificadoResponse)
def revocar_certificado(
    certificado_id: str,
    datos: CertificadoRevocarRequest,
    servicio: CertificadoService = Depends(get_certificado_service),
    usuario: Usuario = Depends(_PUEDE_ESCRIBIR),
) -> CertificadoResponse:
    """`motivo` obligatorio; `version` debe coincidir con la versión
    actual (Optimistic Locking)."""
    return servicio.revocar(certificado_id, datos, usuario_id=usuario.id)
