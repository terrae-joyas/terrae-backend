"""Interfaz del repositorio de joyas."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.joya import EstadoJoya, Joya, TipoJoya


class JoyaRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, joya_id: str) -> Joya | None: ...

    @abstractmethod
    def obtener_por_referencia(self, referencia: str) -> Joya | None: ...

    @abstractmethod
    def crear(self, joya: Joya) -> Joya: ...

    @abstractmethod
    def actualizar(self, joya: Joya) -> Joya: ...

    @abstractmethod
    def listar(
        self,
        offset: int,
        limit: int,
        tipo: TipoJoya | None = None,
        estado: EstadoJoya | None = None,
        sucursal_id: str | None = None,
        esmeralda_id: str | None = None,
    ) -> tuple[list[Joya], int]:
        """Devuelve (elementos_de_la_pagina, total_que_cumple_el_filtro)."""
        ...
