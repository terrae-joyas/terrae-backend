"""
Servicio de aplicación: autenticación.

Orquesta el dominio (entidad Usuario), la infraestructura (hashing,
JWT, repositorio) y expone casos de uso completos que el router HTTP
simplemente invoca y traduce a respuestas. Ningún detalle de FastAPI
vive aquí.
"""

from __future__ import annotations

from datetime import timedelta

from app.application.dto.auth_dto import (
    LoginRequest,
    RegistroRequest,
    TokenResponse,
    UsuarioResponse,
)
from app.application.services.exceptions import (
    CorreoYaRegistradoError,
    CredencialesInvalidasError,
    UsuarioInactivoError,
    UsuarioNoEncontradoError,
)
from app.domain.entities.user import RolUsuario, Usuario
from app.domain.repositories.user_repository import UsuarioRepository
from app.infrastructure.security.jwt_handler import JWTHandler, TipoToken, TokenInvalidoError
from app.infrastructure.security.password_hasher import hash_password, verificar_password


class AuthService:
    def __init__(
        self,
        repositorio: UsuarioRepository,
        jwt_handler: JWTHandler,
        access_token_expira_minutos: int,
        refresh_token_expira_dias: int,
    ) -> None:
        self._repo = repositorio
        self._jwt = jwt_handler
        self._access_expira = timedelta(minutes=access_token_expira_minutos)
        self._refresh_expira = timedelta(days=refresh_token_expira_dias)
        self._access_expira_segundos = access_token_expira_minutos * 60

    # --- Casos de uso ---
    def registrar(self, datos: RegistroRequest, rol: RolUsuario = RolUsuario.CLIENTE) -> UsuarioResponse:
        if self._repo.obtener_por_correo(datos.correo):
            raise CorreoYaRegistradoError(f"El correo {datos.correo} ya está registrado")

        usuario = Usuario(
            nombre_completo=datos.nombre_completo,
            correo=str(datos.correo).strip().lower(),
            hashed_password=hash_password(datos.password),
            rol=rol,
        )
        self._repo.crear(usuario)
        return self._a_response(usuario)

    def autenticar(self, datos: LoginRequest) -> TokenResponse:
        usuario = self._repo.obtener_por_correo(str(datos.correo))
        if usuario is None or not verificar_password(datos.password, usuario.hashed_password):
            raise CredencialesInvalidasError("Correo o contraseña incorrectos")
        if not usuario.activo:
            raise UsuarioInactivoError("El usuario está inactivo. Contacte a un administrador.")

        return self._emitir_tokens(usuario)

    def refrescar(self, refresh_token: str) -> TokenResponse:
        try:
            payload = self._jwt.decodificar_token(refresh_token, TipoToken.REFRESH)
        except TokenInvalidoError as exc:
            raise CredencialesInvalidasError(str(exc)) from exc

        usuario = self._repo.obtener_por_id(payload["sub"])
        if usuario is None:
            raise UsuarioNoEncontradoError("El usuario del refresh token ya no existe")
        if not usuario.activo:
            raise UsuarioInactivoError("El usuario está inactivo. Contacte a un administrador.")

        return self._emitir_tokens(usuario)

    def obtener_usuario_desde_access_token(self, access_token: str) -> Usuario:
        try:
            payload = self._jwt.decodificar_token(access_token, TipoToken.ACCESS)
        except TokenInvalidoError as exc:
            raise CredencialesInvalidasError(str(exc)) from exc

        usuario = self._repo.obtener_por_id(payload["sub"])
        if usuario is None:
            raise UsuarioNoEncontradoError("El usuario del token ya no existe")
        if not usuario.activo:
            raise UsuarioInactivoError("El usuario está inactivo. Contacte a un administrador.")
        return usuario

    # --- Helpers internos ---
    def _emitir_tokens(self, usuario: Usuario) -> TokenResponse:
        access_token = self._jwt.crear_token(
            subject=usuario.id,
            rol=usuario.rol.value,
            tipo=TipoToken.ACCESS,
            expira_en=self._access_expira,
        )
        refresh_token = self._jwt.crear_token(
            subject=usuario.id,
            rol=usuario.rol.value,
            tipo=TipoToken.REFRESH,
            expira_en=self._refresh_expira,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._access_expira_segundos,
        )

    @staticmethod
    def _a_response(usuario: Usuario) -> UsuarioResponse:
        return UsuarioResponse(
            id=usuario.id,
            nombre_completo=usuario.nombre_completo,
            correo=usuario.correo,
            rol=usuario.rol,
            activo=usuario.activo,
            creado_en=usuario.creado_en,
        )
