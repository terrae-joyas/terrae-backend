"""
Interfaz del repositorio de usuarios (Repository Pattern).

Cualquier mecanismo de persistencia (JSON hoy, PostgreSQL desde la
Etapa 5) debe implementar esta interfaz. La capa de aplicación
(`AuthService`) depende únicamente de esta abstracción, nunca de una
implementación concreta — eso se resuelve en `app/dependencies.py`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.user import Usuario


class UsuarioRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, usuario_id: str) -> Usuario | None: ...

    @abstractmethod
    def obtener_por_correo(self, correo: str) -> Usuario | None: ...

    @abstractmethod
    def crear(self, usuario: Usuario) -> Usuario: ...

    @abstractmethod
    def listar_todos(self) -> list[Usuario]: ...

    @abstractmethod
    def actualizar(self, usuario: Usuario) -> Usuario: ...

    @abstractmethod
    def sembrar_si_vacio(self, usuarios_semilla: list[Usuario]) -> None:
        """Inserta usuarios de referencia solo si el repositorio está
        vacío. No debe sobreescribir datos existentes."""
        ...
