"""
Middleware de logging empresarial (Etapa 7.5).

Registra, por cada request HTTP, una línea JSON estructurada con:
request_id, usuario (si el token es válido — best-effort, no fuerza
autenticación), endpoint, método, código de estado, duración en ms, y
la excepción si la hubo.

Cambio de comportamiento observable (aditivo, no rompe contratos):
- Agrega el header de respuesta `X-Request-ID` a TODAS las respuestas.
- No modifica el cuerpo, código de estado, ni ningún otro header de
  ninguna respuesta existente.
"""

from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

from app.infrastructure.logging.structured_logger import get_logger

logger = get_logger("http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        inicio = time.perf_counter()

        usuario_id = self._extraer_usuario_best_effort(request)

        try:
            response = await call_next(request)
        except Exception as exc:  # noqa: BLE001 — se relanza tras loguear
            duracion_ms = round((time.perf_counter() - inicio) * 1000, 2)
            logger.error(
                "Error no controlado procesando request",
                extra={
                    "request_id": request_id,
                    "usuario_id": usuario_id,
                    "endpoint": request.url.path,
                    "metodo": request.method,
                    "duracion_ms": duracion_ms,
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise

        duracion_ms = round((time.perf_counter() - inicio) * 1000, 2)
        nivel_log = logger.warning if response.status_code >= 400 else logger.info
        nivel_log(
            "Request procesado",
            extra={
                "request_id": request_id,
                "usuario_id": usuario_id,
                "endpoint": request.url.path,
                "metodo": request.method,
                "status_code": response.status_code,
                "duracion_ms": duracion_ms,
            },
        )

        response.headers["X-Request-ID"] = request_id
        return response

    @staticmethod
    def _extraer_usuario_best_effort(request: Request) -> str | None:
        """Decodifica el access_token del header Authorization solo para
        fines de logging/auditoría, sin exigir autenticación aquí — cada
        endpoint sigue controlando su propio acceso vía
        `Depends(get_current_user)`. Cualquier error (token ausente,
        inválido o expirado) se ignora silenciosamente: este middleware
        nunca debe ser la causa de que un request falle."""
        auth_header = request.headers.get("authorization", "")
        if not auth_header.lower().startswith("bearer "):
            return None
        token = auth_header[7:].strip()
        try:
            from app.dependencies import get_jwt_handler
            from app.infrastructure.security.jwt_handler import TipoToken

            payload = get_jwt_handler().decodificar_token(token, TipoToken.ACCESS)
            return payload.get("sub")
        except Exception:  # noqa: BLE001 — best-effort, nunca debe romper el request
            return None
