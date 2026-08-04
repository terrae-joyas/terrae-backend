"""Router de autenticación: /api/v1/auth/*"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.dependencies import get_current_user, require_roles
from app.application.dto.auth_dto import (
    LoginRequest,
    RefrescarTokenRequest,
    RegistroRequest,
    TokenResponse,
    UsuarioResponse,
)
from app.application.services.auth_service import AuthService
from app.application.services.exceptions import (
    CorreoYaRegistradoError,
    CredencialesInvalidasError,
    UsuarioInactivoError,
    UsuarioNoEncontradoError,
)
from app.dependencies import get_auth_service
from app.domain.entities.user import RolUsuario, Usuario

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/registro",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario (rol 'cliente' por defecto)",
)
def registrar(
    datos: RegistroRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> UsuarioResponse:
    try:
        return auth_service.registrar(datos, rol=RolUsuario.CLIENTE)
    except CorreoYaRegistradoError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión y obtener access_token + refresh_token",
)
def login(
    datos: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        return auth_service.autenticar(datos)
    except CredencialesInvalidasError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except UsuarioInactivoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.post(
    "/refrescar",
    response_model=TokenResponse,
    summary="Obtener un nuevo access_token a partir de un refresh_token válido",
)
def refrescar(
    datos: RefrescarTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        return auth_service.refrescar(datos.refresh_token)
    except (CredencialesInvalidasError, UsuarioNoEncontradoError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except UsuarioInactivoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.get(
    "/yo",
    response_model=UsuarioResponse,
    summary="Obtener los datos del usuario autenticado",
)
def yo(usuario: Usuario = Depends(get_current_user)) -> UsuarioResponse:
    return UsuarioResponse(
        id=usuario.id,
        nombre_completo=usuario.nombre_completo,
        correo=usuario.correo,
        rol=usuario.rol,
        activo=usuario.activo,
        creado_en=usuario.creado_en,
    )


@router.get(
    "/solo-administradores",
    summary="Endpoint de demostración: requiere rol administrador",
)
def solo_administradores(
    usuario: Usuario = Depends(require_roles(RolUsuario.ADMINISTRADOR)),
) -> dict:
    return {
        "mensaje": f"Hola {usuario.nombre_completo}, tienes acceso de administrador.",
    }
