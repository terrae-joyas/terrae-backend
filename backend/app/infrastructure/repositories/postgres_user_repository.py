"""
Implementación del repositorio de usuarios respaldada por PostgreSQL.

Cumple exactamente la interfaz `UsuarioRepository` (dominio), igual que
`JsonUsuarioRepository`. Esta es la implementación real de producción a
partir de la Etapa 5; `JsonUsuarioRepository` se conserva en el código
(y en sus pruebas) como referencia de la Etapa 4 y como opción de
arranque rápido sin Docker/PostgreSQL.
"""

from __future__ import annotations

from sqlalchemy.orm import Session, sessionmaker

from app.domain.entities.user import RolUsuario, Usuario
from app.domain.repositories.user_repository import UsuarioRepository
from app.infrastructure.db.models.usuarios import UsuarioModel


class PostgresUsuarioRepository(UsuarioRepository):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    # --- Mapeo modelo ORM <-> entidad de dominio ---
    @staticmethod
    def _a_entidad(modelo: UsuarioModel) -> Usuario:
        return Usuario(
            id=modelo.id,
            nombre_completo=modelo.nombre_completo,
            correo=modelo.correo,
            hashed_password=modelo.hashed_password,
            rol=RolUsuario(modelo.rol),
            activo=modelo.activo,
            creado_en=modelo.creado_en,
        )

    @staticmethod
    def _a_modelo(usuario: Usuario) -> UsuarioModel:
        return UsuarioModel(
            id=usuario.id,
            nombre_completo=usuario.nombre_completo,
            correo=usuario.correo,
            hashed_password=usuario.hashed_password,
            rol=usuario.rol.value,
            activo=usuario.activo,
            creado_en=usuario.creado_en,
        )

    # --- UsuarioRepository ---
    def obtener_por_id(self, usuario_id: str) -> Usuario | None:
        with self._session_factory() as session:
            modelo = session.get(UsuarioModel, usuario_id)
            return self._a_entidad(modelo) if modelo else None

    def obtener_por_correo(self, correo: str) -> Usuario | None:
        correo_normalizado = correo.strip().lower()
        with self._session_factory() as session:
            modelo = (
                session.query(UsuarioModel)
                .filter(UsuarioModel.correo == correo_normalizado)
                .one_or_none()
            )
            return self._a_entidad(modelo) if modelo else None

    def crear(self, usuario: Usuario) -> Usuario:
        with self._session_factory() as session:
            modelo = self._a_modelo(usuario)
            session.add(modelo)
            session.commit()
        return usuario

    def listar_todos(self) -> list[Usuario]:
        with self._session_factory() as session:
            modelos = session.query(UsuarioModel).all()
            return [self._a_entidad(m) for m in modelos]

    def actualizar(self, usuario: Usuario) -> Usuario:
        with self._session_factory() as session:
            modelo = session.get(UsuarioModel, usuario.id)
            if modelo is None:
                raise ValueError(f"Usuario {usuario.id} no existe, no se puede actualizar")
            modelo.nombre_completo = usuario.nombre_completo
            modelo.correo = usuario.correo
            modelo.hashed_password = usuario.hashed_password
            modelo.rol = usuario.rol.value
            modelo.activo = usuario.activo
            session.commit()
        return usuario

    def sembrar_si_vacio(self, usuarios_semilla: list[Usuario]) -> None:
        """Inserta usuarios de referencia solo si la tabla está vacía."""
        with self._session_factory() as session:
            existe_alguno = session.query(UsuarioModel.id).first() is not None
            if existe_alguno:
                return
            session.add_all(self._a_modelo(u) for u in usuarios_semilla)
            session.commit()
