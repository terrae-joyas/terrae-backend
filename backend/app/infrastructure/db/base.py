"""
Base declarativa de SQLAlchemy para todos los modelos ORM del backend.

La convención de nombres (`naming_convention`) es importante: sin ella,
Alembic genera nombres de constraints aleatorios/inconsistentes entre
entornos, lo que rompe `alembic downgrade` y las migraciones futuras.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
