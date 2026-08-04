"""Interfaz del repositorio de activos multimedia (Etapa 10)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.activo_multimedia import ActivoMultimedia, TipoActivoMultimedia


class ActivoMultimediaRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, activo_id: str) -> ActivoMultimedia | None: ...

    @abstractmethod
    def crear(self, activo: ActivoMultimedia, usuario_id: str | None) -> ActivoMultimedia: ...

    @abstractmethod
    def desactivar(self, activo_id: str, usuario_id: str | None) -> ActivoMultimedia:
        """Baja lógica — un activo multimedia nunca se borra
        físicamente (rompería la trazabilidad que es su propósito)."""
        ...

    @abstractmethod
    def listar(
        self,
        offset: int,
        limit: int,
        entidad_tipo: str | None = None,
        entidad_id: str | None = None,
        tipo: TipoActivoMultimedia | None = None,
    ) -> tuple[list[ActivoMultimedia], int]:
        """Devuelve (elementos_de_la_pagina, total_que_cumple_el_filtro)."""
        ...
