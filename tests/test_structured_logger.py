"""Pruebas del logging estructurado (Etapa 7.5)."""

from __future__ import annotations

import json
import logging

from app.infrastructure.logging.structured_logger import FormateadorJSON, get_logger


def _formatear(record: logging.LogRecord) -> dict:
    return json.loads(FormateadorJSON().format(record))


def _crear_record(msg: str, **extra) -> logging.LogRecord:
    record = logging.LogRecord(
        name="terrae.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=(),
        exc_info=None,
    )
    for k, v in extra.items():
        setattr(record, k, v)
    return record


def test_formateador_json_produce_json_valido_con_campos_base():
    record = _crear_record("Sucursal creada")
    payload = _formatear(record)

    assert payload["mensaje"] == "Sucursal creada"
    assert payload["nivel"] == "info"
    assert payload["logger"] == "terrae.test"
    assert "timestamp" in payload


def test_formateador_json_incluye_campos_extra_de_contexto():
    record = _crear_record(
        "Request procesado",
        request_id="req-123",
        usuario_id="user-1",
        endpoint="/api/v1/sucursales",
        duracion_ms=12.5,
    )
    payload = _formatear(record)

    assert payload["request_id"] == "req-123"
    assert payload["usuario_id"] == "user-1"
    assert payload["endpoint"] == "/api/v1/sucursales"
    assert payload["duracion_ms"] == 12.5


def test_formateador_json_incluye_excepcion_si_hay_exc_info():
    try:
        raise ValueError("algo falló")
    except ValueError:
        import sys

        record = logging.LogRecord(
            name="terrae.test",
            level=logging.ERROR,
            pathname=__file__,
            lineno=1,
            msg="Error procesando",
            args=(),
            exc_info=sys.exc_info(),
        )
    payload = _formatear(record)
    assert "excepcion" in payload
    assert "ValueError" in payload["excepcion"]


def test_get_logger_devuelve_logger_con_prefijo_terrae():
    logger = get_logger("mi_modulo")
    assert logger.name == "terrae.mi_modulo"


def test_get_logger_reutiliza_el_mismo_handler_entre_llamadas():
    logger1 = get_logger("modulo_a")
    logger2 = get_logger("modulo_b")
    # Ambos cuelgan del mismo logger raíz "terrae" configurado una sola vez
    raiz = logging.getLogger("terrae")
    assert len(raiz.handlers) == 1
    assert logger1.name != logger2.name
