"""
Registro centralizado de manejadores de excepciones.

Traduce las excepciones de `app.application.errors` a respuestas HTTP
consistentes en toda la API, con el mismo contrato de siempre:
`{"detail": "<mensaje>"}`. Se registra una única vez en `app/main.py`.
"""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.application.errors import (
    EntidadDuplicadaError,
    EntidadNoEncontradaError,
    OperacionNoPermitidaError,
    ValidacionNegocioError,
)

_MAPA_EXCEPCIONES = {
    EntidadNoEncontradaError: status.HTTP_404_NOT_FOUND,
    EntidadDuplicadaError: status.HTTP_409_CONFLICT,
    OperacionNoPermitidaError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    ValidacionNegocioError: status.HTTP_422_UNPROCESSABLE_ENTITY,
}


def registrar_manejadores_de_errores(app: FastAPI) -> None:
    for tipo_excepcion, status_code in _MAPA_EXCEPCIONES.items():

        def _crear_handler(codigo: int):
            async def _handler(request: Request, exc: Exception) -> JSONResponse:
                return JSONResponse(status_code=codigo, content={"detail": str(exc)})

            return _handler

        app.add_exception_handler(tipo_excepcion, _crear_handler(status_code))
