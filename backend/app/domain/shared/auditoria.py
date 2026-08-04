"""
Campos de auditoría transversales (Etapa 7.5).

`CamposAuditoria` es un mixin de dataclass pensado para que las
entidades de dominio de las etapas 8 en adelante lo incluyan por
composición o herencia, sin duplicar estos 6 campos en cada entidad
nueva.

Uso recomendado (herencia con `kw_only=True`, evita problemas de orden
de campos con dataclasses):

    @dataclass(kw_only=True)
    class Esmeralda(CamposAuditoria):
        codigo_interno: str
        mina_origen: MinaOrigen
        ...

Deliberadamente NO se aplica a las entidades ya existentes
(`Usuario`, `Sucursal`, `Joya`, `Esmeralda`) en esta etapa: hacerlo
exigiría migrar sus tablas (columnas nuevas, backfill de datos) y
tocar servicios/repositorios ya probados — fuera del alcance de una
etapa que, por mandato explícito, no debe romper compatibilidad ni
reescribir módulos terminados. Verlo como una convención a aplicar
"hacia adelante" a partir de la Etapa 8, y como oportunidad de
adopción retroactiva cuando cada entidad existente lo requiera por
una necesidad real de negocio (no solo por consistencia cosmética).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(kw_only=True)
class CamposAuditoria:
    creado_en: datetime | None = None
    actualizado_en: datetime | None = None
    creado_por: str | None = None  # id de Usuario
    actualizado_por: str | None = None  # id de Usuario
    eliminado_en: datetime | None = None
    eliminado_por: str | None = None  # id de Usuario

    @property
    def esta_eliminado(self) -> bool:
        """Baja lógica genérica. Ver docs/CONVENCIONES_ENTIDADES.md:
        entidades con ciclo de vida propio (ej. Joya y su máquina de
        estados) NO deben usar esto — `eliminado_en` es para el caso
        genérico de "activo/inactivo" sin estados intermedios."""
        return self.eliminado_en is not None
