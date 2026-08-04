"""
Dependencias de FastAPI para proteger endpoints.

Uso típico en un router:

    @router.get("/algo-protegido")
    def endpoint(usuario: Usuario = Depends(get_current_user)):
        ...

    @router.delete("/solo-admin/{id}")
    def endpoint(usuario: Usuario = Depends(require_roles(RolUsuario.ADMINISTRADOR))):
        ...
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.services.exceptions import (
    CredencialesInvalidasError,
    UsuarioInactivoError,
    UsuarioNoEncontradoError,
)
from app.domain.entities.user import RolUsuario, Usuario
from app.dependencies import get_auth_service

_bearer_scheme = HTTPBearer(
    scheme_name="BearerAuth",
    description="Access token JWT obtenido en /api/v1/auth/login",
)


def get_current_user(
    credenciales: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> Usuario:
    auth_service = get_auth_service()
    try:
        return auth_service.obtener_usuario_desde_access_token(credenciales.credentials)
    except (CredencialesInvalidasError, UsuarioNoEncontradoError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except UsuarioInactivoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


def require_roles(*roles_permitidos: RolUsuario):
    """Factory de dependencia: exige que el usuario autenticado tenga
    alguno de los roles indicados."""

    def _verificar(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if usuario.rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"El rol '{usuario.rol.value}' no tiene permiso para esta acción. "
                    f"Roles permitidos: {', '.join(r.value for r in roles_permitidos)}."
                ),
            )
        return usuario

    return _verificar
