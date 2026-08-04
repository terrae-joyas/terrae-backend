"""
Configuración de entorno de Alembic.

Toma la URL de base de datos de `app.config.get_settings()` (la misma
fuente de verdad que usa el backend en runtime, vía `.env` /
docker-compose) en vez de duplicarla en `alembic.ini`, y usa
`Base.metadata` (con todos los modelos ya importados) para el
autogenerate de migraciones futuras.
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Aseguramos que el paquete `app` sea importable (Alembic se ejecuta
# desde backend/, donde vive `app/`).
from app.config import get_settings
from app.infrastructure.db.base import Base

# Importa TODOS los modelos para que Base.metadata los conozca.
import app.infrastructure.db.models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_database_url() -> str:
    settings = get_settings()
    if not settings.database_url:
        raise RuntimeError(
            "DATABASE_URL no configurada — no se puede ejecutar Alembic. "
            "Revisa el archivo .env o las variables de docker-compose."
        )
    return settings.database_url


def run_migrations_offline() -> None:
    """Genera el SQL de la migración sin conectarse a la base de datos
    (`alembic upgrade --sql`)."""
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica las migraciones conectándose realmente a la base de datos."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
