"""
Entidad de dominio: Usuario.

Regla de Clean Architecture: esta clase no importa nada de FastAPI,
Pydantic, JSON ni PostgreSQL. Es lógica de negocio pura.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class RolUsuario(str, Enum):
    """Roles soportados por el ecosistema Terrae.

    - ADMINISTRADOR: control total del backoffice (usuarios, auditoría, config).
    - JOYERO: gestiona piezas, inventario y certificados de su(s) taller(es).
    - AUDITOR: acceso de solo lectura a trazabilidad, blockchain y logs.
    - CLIENTE: acceso a su(s) pasaporte(s) digital(es) y garantías.
    """

    ADMINISTRADOR = "administrador"
    JOYERO = "joyero"
    AUDITOR = "auditor"
    CLIENTE = "cliente"


@dataclass
class Usuario:
    nombre_completo: str
    correo: str
    hashed_password: str
    rol: RolUsuario = RolUsuario.CLIENTE
    activo: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))
    creado_en: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def es_administrador(self) -> bool:
        return self.rol == RolUsuario.ADMINISTRADOR
