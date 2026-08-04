"""Interfaz del repositorio de inventario (Etapa 9)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.inventario import Inventario


class InventarioRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, inventario_id: str) -> Inventario | None: ...

    @abstractmethod
    def obtener_por_joya_id(self, joya_id: str) -> Inventario | None: ...

    @abstractmethod
    def crear(self, inventario: Inventario, usuario_id: str | None) -> Inventario: ...

    @abstractmethod
    def mover(
        self,
        inventario_id: str,
        sucursal_id: str,
        ubicacion_fisica: str | None,
        version_esperada: int,
        usuario_id: str | None,
    ) -> Inventario:
        """Cambia sucursal/ubicación física (Optimistic Locking). NO
        modifica `cantidad` — ver `ajustar_cantidad` y ADR-009-01."""
        ...

    @abstractmethod
    def ajustar_cantidad(
        self,
        inventario_id: str,
        delta: int,
        version_esperada: int,
        usuario_id: str | None,
    ) -> Inventario:
        """Ajuste atómico basado en delta (ADR-009-01). Levanta
        `ConflictoDeVersionError` si la versión no coincide, o
        `ValidacionNegocioError` si el resultado sería negativo."""
        ...

    @abstractmethod
    def listar(
        self,
        offset: int,
        limit: int,
        sucursal_id: str | None = None,
        joya_id: str | None = None,
        cantidad_min: int | None = None,
    ) -> tuple[list[Inventario], int]:
        """Devuelve (elementos_de_la_pagina, total_que_cumple_el_filtro)."""
        ...
