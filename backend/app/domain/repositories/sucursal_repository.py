"""Interfaz del repositorio de sucursales (Repository Pattern).

A diferencia de `UsuarioRepository` (Etapa 4, con implementación JSON y
PostgreSQL), a partir de esta etapa las entidades nuevas solo tienen
implementación PostgreSQL: la base de datos ya es parte estable de la
infraestructura desde la Etapa 5, así que mantener un doble camino
JSON/PostgreSQL para cada entidad nueva sería complejidad sin beneficio
real. La interfaz igual se mantiene (Clean Architecture, testeable con
SQLite en memoria como en `test_postgres_user_repository.py`).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.sucursal import Sucursal, TipoSucursal


class SucursalRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, sucursal_id: str) -> Sucursal | None: ...

    @abstractmethod
    def crear(self, sucursal: Sucursal) -> Sucursal: ...

    @abstractmethod
    def actualizar(self, sucursal: Sucursal) -> Sucursal: ...

    @abstractmethod
    def listar(
        self,
        offset: int,
        limit: int,
        tipo: TipoSucursal | None = None,
        ciudad: str | None = None,
        activa: bool | None = None,
    ) -> tuple[list[Sucursal], int]:
        """Devuelve (elementos_de_la_pagina, total_que_cumple_el_filtro)."""
        ...
