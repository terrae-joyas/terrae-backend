"""
Logging estructurado (Etapa 7.5).

Formatea cada línea de log como un objeto JSON de una sola línea, apto
para ingestión directa por herramientas de observabilidad (CloudWatch,
Datadog, ELK, etc.) sin parseo adicional. Reutilizable por cualquier
módulo: `get_logger(__name__).info("mensaje", extra={"usuario_id": ...})`.

No reemplaza el logging estándar de FastAPI/uvicorn (accesos HTTP
crudos); complementa con contexto de negocio a través de
`RequestLoggingMiddleware` (ver `app/api/v1/middleware/request_logging.py`).
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

_CAMPOS_RESERVADOS_LOGRECORD = {
    "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
    "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
    "created", "msecs", "relativeCreated", "thread", "threadName",
    "processName", "process", "message", "taskName",
}


class FormateadorJSON(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "nivel": record.levelname.lower(),
            "logger": record.name,
            "mensaje": record.getMessage(),
        }

        # Campos de contexto pasados vía `extra={...}` (request_id,
        # usuario_id, endpoint, accion, duracion_ms, etc.)
        for clave, valor in record.__dict__.items():
            if clave not in _CAMPOS_RESERVADOS_LOGRECORD and not clave.startswith("_"):
                payload[clave] = valor

        if record.exc_info:
            payload["excepcion"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, default=str)


@lru_cache
def _configurar_root() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(FormateadorJSON())

    root = logging.getLogger("terrae")
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    root.propagate = False


def get_logger(nombre: str) -> logging.Logger:
    """Logger estructurado con prefijo `terrae.<nombre>`. Uso:

        logger = get_logger(__name__)
        logger.info("Sucursal creada", extra={"sucursal_id": id, "usuario_id": uid})
    """
    _configurar_root()
    return logging.getLogger(f"terrae.{nombre}")
