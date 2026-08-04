"""
Excepciones genéricas de la capa de aplicación.

Convención desde la Etapa 6: cualquier servicio de dominio nuevo
(sucursales, joyas, esmeraldas, certificados...) levanta estas
excepciones en vez de `HTTPException` directamente. Los routers no
necesitan `try/except` — `app/api/v1/error_handlers.py` las traduce a
respuestas HTTP consistentes de forma centralizada.

(El módulo `auth` de la Etapa 4 usa sus propias excepciones locales por
motivos históricos — se mantienen así para no tocar código ya probado —
pero todo router nuevo a partir de esta etapa debe usar este módulo.)
"""


class ErrorAplicacion(Exception):
    """Base de todas las excepciones de la capa de aplicación."""


class EntidadNoEncontradaError(ErrorAplicacion):
    """El recurso solicitado no existe → HTTP 404."""


class EntidadDuplicadaError(ErrorAplicacion):
    """Conflicto de unicidad (ej. código ya registrado) → HTTP 409."""


class OperacionNoPermitidaError(ErrorAplicacion):
    """La operación es válida pero no está permitida en el estado actual
    de la entidad (ej. desactivar una sucursal con inventario activo) →
    HTTP 422."""


class ValidacionNegocioError(ErrorAplicacion):
    """La entrada es sintácticamente válida pero viola una regla de
    negocio no expresable solo con Pydantic → HTTP 422."""
