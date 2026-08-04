"""
Inyección de dependencias del backend Terrae.

Etapa 5: `get_usuario_repository()` elige la implementación según
`settings.database_url`. Este es exactamente el cambio prometido desde
la Etapa 4: ni `AuthService`, ni los routers, ni las dependencias de la
API (`app/api/v1/dependencies.py`) se modificaron para soportar
PostgreSQL — solo este archivo.

Etapa 6: `get_sucursal_repository()`/`get_sucursal_service()` siguen el
mismo patrón de wiring, pero sin fallback JSON — ver nota en
`app/domain/repositories/sucursal_repository.py` sobre por qué las
entidades nuevas a partir de esta etapa van directo a PostgreSQL.
"""

from __future__ import annotations

from functools import lru_cache

from app.application.services.activo_multimedia_service import ActivoMultimediaService
from app.application.services.auth_service import AuthService
from app.application.services.certificado_service import CertificadoService
from app.application.services.esmeralda_service import EsmeraldaService
from app.application.services.inventario_service import InventarioService
from app.application.services.joya_service import JoyaService
from app.application.services.sucursal_service import SucursalService
from app.config import get_settings
from app.domain.entities.user import RolUsuario, Usuario
from app.domain.repositories.activo_multimedia_repository import ActivoMultimediaRepository
from app.domain.repositories.certificado_repository import CertificadoRepository
from app.domain.repositories.esmeralda_repository import EsmeraldaRepository
from app.domain.repositories.inventario_repository import InventarioRepository
from app.domain.repositories.joya_repository import JoyaRepository
from app.domain.repositories.sucursal_repository import SucursalRepository
from app.domain.repositories.user_repository import UsuarioRepository
from app.infrastructure.db.session import get_session_factory
from app.infrastructure.events.event_bus import EventBus, InMemoryEventBus
from app.infrastructure.events.version_registry import (
    HistorialEventoRegistradorVersion,
    RegistradorVersion,
)
from app.infrastructure.repositories.json_user_repository import JsonUsuarioRepository
from app.infrastructure.repositories.postgres_activo_multimedia_repository import (
    PostgresActivoMultimediaRepository,
)
from app.infrastructure.repositories.postgres_certificado_repository import PostgresCertificadoRepository
from app.infrastructure.repositories.postgres_esmeralda_repository import PostgresEsmeraldaRepository
from app.infrastructure.repositories.postgres_inventario_repository import PostgresInventarioRepository
from app.infrastructure.repositories.postgres_joya_repository import PostgresJoyaRepository
from app.infrastructure.repositories.postgres_sucursal_repository import PostgresSucursalRepository
from app.infrastructure.repositories.postgres_user_repository import PostgresUsuarioRepository
from app.infrastructure.security.jwt_handler import JWTHandler
from app.infrastructure.security.password_hasher import hash_password


@lru_cache
def get_usuario_repository() -> UsuarioRepository:
    settings = get_settings()

    if settings.database_url:
        # Camino real de producción/Docker (Etapa 5 en adelante).
        repo: UsuarioRepository = PostgresUsuarioRepository(get_session_factory())
    else:
        # Fallback de desarrollo rápido sin PostgreSQL (ej. correr el
        # backend fuera de Docker sin levantar la base de datos). Se
        # conserva por compatibilidad con la Etapa 4, no es el camino
        # recomendado a partir de esta etapa.
        repo = JsonUsuarioRepository(settings.usuarios_data_path)

    _sembrar_usuarios_demo(repo)
    return repo


@lru_cache
def get_jwt_handler() -> JWTHandler:
    settings = get_settings()
    return JWTHandler(secret_key=settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


@lru_cache
def get_auth_service() -> AuthService:
    settings = get_settings()
    return AuthService(
        repositorio=get_usuario_repository(),
        jwt_handler=get_jwt_handler(),
        access_token_expira_minutos=settings.jwt_access_token_expire_minutes,
        refresh_token_expira_dias=settings.jwt_refresh_token_expire_days,
    )


@lru_cache
def get_sucursal_repository() -> SucursalRepository:
    return PostgresSucursalRepository(get_session_factory())


@lru_cache
def get_sucursal_service() -> SucursalService:
    return SucursalService(get_sucursal_repository())


@lru_cache
def get_esmeralda_repository() -> EsmeraldaRepository:
    return PostgresEsmeraldaRepository(get_session_factory())


@lru_cache
def get_joya_repository() -> JoyaRepository:
    return PostgresJoyaRepository(get_session_factory())


@lru_cache
def get_joya_service() -> JoyaService:
    return JoyaService(
        repositorio=get_joya_repository(),
        esmeralda_repositorio=get_esmeralda_repository(),
        sucursal_repositorio=get_sucursal_repository(),
    )


@lru_cache
def get_event_bus() -> EventBus:
    """Bus de Domain Events (Etapa 7.5). Desde la Etapa 8 tiene un
    consumidor real registrado en el arranque de la app — ver
    `app/main.py::configurar_event_bus` y ADR-008-03."""
    return InMemoryEventBus()


@lru_cache
def get_registrador_version() -> RegistradorVersion:
    """Registrador de versiones (Etapa 7.5, ADR-008-01). Reutiliza
    `historial_eventos`, sin tabla nueva."""
    return HistorialEventoRegistradorVersion(get_session_factory())


@lru_cache
def get_esmeralda_service() -> EsmeraldaService:
    return EsmeraldaService(
        repositorio=get_esmeralda_repository(),
        event_bus=get_event_bus(),
        registrador_version=get_registrador_version(),
    )


@lru_cache
def get_inventario_repository() -> InventarioRepository:
    return PostgresInventarioRepository(get_session_factory())


@lru_cache
def get_inventario_service() -> InventarioService:
    return InventarioService(
        repositorio=get_inventario_repository(),
        joya_repositorio=get_joya_repository(),
        sucursal_repositorio=get_sucursal_repository(),
        event_bus=get_event_bus(),
        registrador_version=get_registrador_version(),
    )


@lru_cache
def get_certificado_repository() -> CertificadoRepository:
    return PostgresCertificadoRepository(get_session_factory())


@lru_cache
def get_certificado_service() -> CertificadoService:
    return CertificadoService(
        repositorio=get_certificado_repository(),
        joya_repositorio=get_joya_repository(),
        event_bus=get_event_bus(),
        registrador_version=get_registrador_version(),
    )


@lru_cache
def get_activo_multimedia_repository() -> ActivoMultimediaRepository:
    return PostgresActivoMultimediaRepository(get_session_factory())


@lru_cache
def get_activo_multimedia_service() -> ActivoMultimediaService:
    """Registra validadores de existencia para los `entidad_tipo`
    conocidos (ADR-010-01) — extensible sin modificar
    `ActivoMultimediaService` cuando aparezcan tipos nuevos."""
    servicio = ActivoMultimediaService(
        repositorio=get_activo_multimedia_repository(),
        event_bus=get_event_bus(),
        registrador_version=get_registrador_version(),
    )
    servicio.registrar_validador("Joya", lambda id_: get_joya_repository().obtener_por_id(id_) is not None)
    servicio.registrar_validador(
        "Esmeralda", lambda id_: get_esmeralda_repository().obtener_por_id(id_) is not None
    )
    servicio.registrar_validador(
        "Certificado", lambda id_: get_certificado_repository().obtener_por_id(id_) is not None
    )
    return servicio


def _sembrar_usuarios_demo(repo: UsuarioRepository) -> None:
    """Crea 4 usuarios de referencia (uno por rol) solo si el
    repositorio está vacío, para poder probar la API y el frontend sin
    pasos manuales adicionales. Contraseña de todos: `Terrae#2026`.
    NUNCA usar estas credenciales en un entorno real.

    Funciona igual sobre `JsonUsuarioRepository` y
    `PostgresUsuarioRepository`: ambas implementan `sembrar_si_vacio`
    como parte de la interfaz `UsuarioRepository`.
    """
    semilla = [
        Usuario(
            nombre_completo="Ana Administradora",
            correo="admin@terrae.co",
            hashed_password=hash_password("Terrae#2026"),
            rol=RolUsuario.ADMINISTRADOR,
        ),
        Usuario(
            nombre_completo="Julián Joyero",
            correo="joyero@terrae.co",
            hashed_password=hash_password("Terrae#2026"),
            rol=RolUsuario.JOYERO,
        ),
        Usuario(
            nombre_completo="Andrea Auditora",
            correo="auditor@terrae.co",
            hashed_password=hash_password("Terrae#2026"),
            rol=RolUsuario.AUDITOR,
        ),
        Usuario(
            nombre_completo="Carlos Cliente",
            correo="cliente@terrae.co",
            hashed_password=hash_password("Terrae#2026"),
            rol=RolUsuario.CLIENTE,
        ),
    ]
    repo.sembrar_si_vacio(semilla)
