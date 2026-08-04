"""
Convención de paginación de la API Terrae.

Todo endpoint de listado (`GET /api/v1/<recurso>`) sigue este mismo
patrón: parámetros `pagina`/`tamano_pagina` vía `Depends(ParametrosPaginacion)`
y respuesta `RespuestaPaginada[T]`. Los routers de dominio de las
etapas 7 en adelante (joyas, esmeraldas, certificados...) deben
reutilizar esto en vez de inventar su propia paginación.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

T = TypeVar("T")

TAMANO_PAGINA_DEFECTO = 20
TAMANO_PAGINA_MAXIMO = 100


class ParametrosPaginacion:
    """Dependencia de FastAPI: `pagina=Depends(ParametrosPaginacion)`.

    `pagina` es 1-indexado (más natural para un cliente/API pública que
    un offset 0-indexado interno).
    """

    def __init__(
        self,
        pagina: int = Query(1, ge=1, description="Número de página (1-indexado)"),
        tamano_pagina: int = Query(
            TAMANO_PAGINA_DEFECTO,
            ge=1,
            le=TAMANO_PAGINA_MAXIMO,
            description=f"Elementos por página (máximo {TAMANO_PAGINA_MAXIMO})",
        ),
    ) -> None:
        self.pagina = pagina
        self.tamano_pagina = tamano_pagina

    @property
    def offset(self) -> int:
        return (self.pagina - 1) * self.tamano_pagina

    @property
    def limit(self) -> int:
        return self.tamano_pagina


class RespuestaPaginada(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(description="Total de elementos que cumplen el filtro, en todas las páginas")
    pagina: int
    tamano_pagina: int
    total_paginas: int

    @classmethod
    def construir(
        cls, items: list[T], total: int, parametros: ParametrosPaginacion
    ) -> "RespuestaPaginada[T]":
        total_paginas = (total + parametros.tamano_pagina - 1) // parametros.tamano_pagina if total else 0
        return cls(
            items=items,
            total=total,
            pagina=parametros.pagina,
            tamano_pagina=parametros.tamano_pagina,
            total_paginas=total_paginas,
        )
