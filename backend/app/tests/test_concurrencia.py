"""Pruebas de la infraestructura de concurrencia optimista (Etapa 7.5)."""

from __future__ import annotations

import pytest

from app.application.concurrencia import ConflictoDeVersionError, verificar_version
from app.application.errors import OperacionNoPermitidaError


def test_verificar_version_no_lanza_error_si_coinciden():
    verificar_version(version_actual=3, version_esperada=3)  # no debe lanzar


def test_verificar_version_lanza_conflicto_si_no_coinciden():
    with pytest.raises(ConflictoDeVersionError):
        verificar_version(version_actual=4, version_esperada=3)


def test_conflicto_de_version_es_subtipo_de_operacion_no_permitida():
    """Garantiza que ConflictoDeVersionError se traduzca automáticamente
    a HTTP 422 vía el mismo manejador genérico de OperacionNoPermitidaError
    (app/api/v1/error_handlers.py), sin necesitar un manejador nuevo."""
    assert issubclass(ConflictoDeVersionError, OperacionNoPermitidaError)


def test_mensaje_de_error_incluye_ambas_versiones():
    with pytest.raises(ConflictoDeVersionError) as exc_info:
        verificar_version(version_actual=5, version_esperada=2)
    mensaje = str(exc_info.value)
    assert "5" in mensaje
    assert "2" in mensaje
