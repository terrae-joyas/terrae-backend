"""
Creación y verificación de JSON Web Tokens (JWT).

Dos tipos de token:
- `access`: de vida corta, se envía en cada request protegido
  (`Authorization: Bearer <token>`).
- `refresh`: de vida larga, se usa únicamente para obtener un nuevo
  access token sin pedir credenciales de nuevo.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

import jwt
from jwt import PyJWTError


class TipoToken(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenInvalidoError(Exception):
    """Se lanza cuando un token es inválido, expiró o su tipo no coincide."""


class JWTHandler:
    def __init__(self, secret_key: str, algorithm: str = "HS256") -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm

    def crear_token(
        self,
        subject: str,
        rol: str,
        tipo: TipoToken,
        expira_en: timedelta,
        claims_extra: dict[str, Any] | None = None,
    ) -> str:
        ahora = datetime.now(timezone.utc)
        payload: dict[str, Any] = {
            "sub": subject,
            "rol": rol,
            "type": tipo.value,
            "iat": ahora,
            "exp": ahora + expira_en,
        }
        if claims_extra:
            payload.update(claims_extra)
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decodificar_token(self, token: str, tipo_esperado: TipoToken) -> dict[str, Any]:
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except PyJWTError as exc:
            raise TokenInvalidoError(f"Token inválido o expirado: {exc}") from exc

        if payload.get("type") != tipo_esperado.value:
            raise TokenInvalidoError(
                f"Tipo de token incorrecto: se esperaba '{tipo_esperado.value}', "
                f"se recibió '{payload.get('type')}'"
            )
        return payload
