"""
Infraestructura de concurrencia optimista (Etapa 7.5 — preparación).

No se aplica a ninguna entidad existente todavía. Cuando una entidad
futura lo necesite (ej. dos joyeros editando la misma joya a la vez),
su servicio de aplicación debe:

1. Incluir `version` en el DTO de actualización (o recibirlo del
   cliente vía header `If-Match`, a definir cuando haya un caso real).
2. Llamar a `verificar_version()` antes de persistir.
3. El repositorio incrementa `version` en cada `UPDATE` (patrón
   estándar: `UPDATE ... SET version = version + 1 WHERE id = :id AND
   version = :version_esperada`, 0 filas afectadas = conflicto).

Esta etapa deja el contrato (excepción + función de verificación)
listo; la implementación del `UPDATE` condicional en cada repositorio
se hace cuando la entidad que lo necesite se construya.
"""

from __future__ import annotations

from app.application.errors import OperacionNoPermitidaError


class ConflictoDeVersionError(OperacionNoPermitidaError):
    """La versión enviada por el cliente no coincide con la versión
    actual del recurso — alguien más lo modificó primero. Se mapea al
    mismo código HTTP que `OperacionNoPermitidaError` (422) mediante
    herencia; un futuro afinamiento podría darle su propio código 409
    si la experiencia de uso lo justifica."""


def verificar_version(version_actual: int, version_esperada: int) -> None:
    if version_actual != version_esperada:
        raise ConflictoDeVersionError(
            f"El recurso fue modificado por otro usuario (versión actual: "
            f"{version_actual}, versión enviada: {version_esperada}). "
            "Vuelve a cargar los datos antes de reintentar."
        )
