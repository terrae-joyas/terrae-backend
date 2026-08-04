"""DTOs de la API de autenticación. Nunca se exponen las entidades de
dominio directamente — siempre se traducen a/desde estos esquemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.domain.entities.user import RolUsuario


class RegistroRequest(BaseModel):
    nombre_completo: str = Field(min_length=2, max_length=120)
    correo: EmailStr
    password: str = Field(min_length=8, max_length=128)
    confirmar_password: str = Field(min_length=8, max_length=128)

    @field_validator("confirmar_password")
    @classmethod
    def passwords_coinciden(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Las contraseñas no coinciden")
        return v


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str


class RefrescarTokenRequest(BaseModel):
    refresh_token: str


class UsuarioResponse(BaseModel):
    id: str
    nombre_completo: str
    correo: str
    rol: RolUsuario
    activo: bool
    creado_en: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos de validez del access_token
