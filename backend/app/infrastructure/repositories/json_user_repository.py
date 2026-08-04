"""
Implementación del repositorio de usuarios basada en un archivo JSON.

Cumple exactamente la interfaz `UsuarioRepository` (dominio). Cuando la
Etapa 5 introduzca PostgreSQL + SQLAlchemy, se creará una
`PostgresUsuarioRepository` que implemente la misma interfaz, y el único
archivo que cambiará será `app/dependencies.py` (el punto donde se
decide qué implementación inyectar). Ningún servicio de aplicación ni
router de la API necesitará modificarse.

Nota de diseño: apta para desarrollo local de una sola instancia. No es
segura para múltiples procesos/instancias concurrentes (esa garantía la
dará PostgreSQL en la Etapa 5); por eso se usa un `threading.Lock` que
solo protege contra condiciones de carrera dentro de un mismo proceso.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime
from pathlib import Path

from app.domain.entities.user import RolUsuario, Usuario
from app.domain.repositories.user_repository import UsuarioRepository

_LOCK = threading.Lock()


class JsonUsuarioRepository(UsuarioRepository):
    def __init__(self, ruta_archivo: str | Path) -> None:
        self._ruta = Path(ruta_archivo)
        self._ruta.parent.mkdir(parents=True, exist_ok=True)
        if not self._ruta.exists():
            self._escribir([])

    # --- Serialización ---
    @staticmethod
    def _a_dict(usuario: Usuario) -> dict:
        return {
            "id": usuario.id,
            "nombre_completo": usuario.nombre_completo,
            "correo": usuario.correo,
            "hashed_password": usuario.hashed_password,
            "rol": usuario.rol.value,
            "activo": usuario.activo,
            "creado_en": usuario.creado_en.isoformat(),
        }

    @staticmethod
    def _desde_dict(data: dict) -> Usuario:
        return Usuario(
            id=data["id"],
            nombre_completo=data["nombre_completo"],
            correo=data["correo"],
            hashed_password=data["hashed_password"],
            rol=RolUsuario(data["rol"]),
            activo=data["activo"],
            creado_en=datetime.fromisoformat(data["creado_en"]),
        )

    def _leer(self) -> list[dict]:
        with open(self._ruta, encoding="utf-8") as f:
            return json.load(f)

    def _escribir(self, registros: list[dict]) -> None:
        with open(self._ruta, "w", encoding="utf-8") as f:
            json.dump(registros, f, ensure_ascii=False, indent=2)

    # --- UsuarioRepository ---
    def obtener_por_id(self, usuario_id: str) -> Usuario | None:
        with _LOCK:
            for reg in self._leer():
                if reg["id"] == usuario_id:
                    return self._desde_dict(reg)
        return None

    def obtener_por_correo(self, correo: str) -> Usuario | None:
        correo_normalizado = correo.strip().lower()
        with _LOCK:
            for reg in self._leer():
                if reg["correo"].strip().lower() == correo_normalizado:
                    return self._desde_dict(reg)
        return None

    def crear(self, usuario: Usuario) -> Usuario:
        with _LOCK:
            registros = self._leer()
            registros.append(self._a_dict(usuario))
            self._escribir(registros)
        return usuario

    def listar_todos(self) -> list[Usuario]:
        with _LOCK:
            return [self._desde_dict(r) for r in self._leer()]

    def actualizar(self, usuario: Usuario) -> Usuario:
        with _LOCK:
            registros = self._leer()
            for i, reg in enumerate(registros):
                if reg["id"] == usuario.id:
                    registros[i] = self._a_dict(usuario)
                    break
            else:
                raise ValueError(f"Usuario {usuario.id} no existe, no se puede actualizar")
            self._escribir(registros)
        return usuario

    def sembrar_si_vacio(self, usuarios_semilla: list[Usuario]) -> None:
        """Inserta usuarios de referencia solo si el repositorio está vacío
        (arranque en limpio). No sobreescribe datos existentes."""
        with _LOCK:
            registros = self._leer()
            if registros:
                return
            self._escribir([self._a_dict(u) for u in usuarios_semilla])
