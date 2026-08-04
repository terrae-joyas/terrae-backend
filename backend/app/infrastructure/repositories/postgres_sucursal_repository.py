"""Implementación PostgreSQL del repositorio de sucursales."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.domain.entities.sucursal import Sucursal, TipoSucursal
from app.domain.repositories.sucursal_repository import SucursalRepository
from app.infrastructure.db.models.organizacion import SucursalModel


class PostgresSucursalRepository(SucursalRepository):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    @staticmethod
    def _a_entidad(modelo: SucursalModel) -> Sucursal:
        return Sucursal(
            id=modelo.id,
            nombre=modelo.nombre,
            tipo=TipoSucursal(modelo.tipo),
            ciudad=modelo.ciudad,
            direccion=modelo.direccion,
            activa=modelo.activa,
            creado_en=modelo.creado_en,
        )

    @staticmethod
    def _a_modelo(sucursal: Sucursal) -> SucursalModel:
        return SucursalModel(
            id=sucursal.id,
            nombre=sucursal.nombre,
            tipo=sucursal.tipo.value,
            ciudad=sucursal.ciudad,
            direccion=sucursal.direccion,
            activa=sucursal.activa,
            creado_en=sucursal.creado_en,
        )

    def obtener_por_id(self, sucursal_id: str) -> Sucursal | None:
        with self._session_factory() as session:
            modelo = session.get(SucursalModel, sucursal_id)
            return self._a_entidad(modelo) if modelo else None

    def crear(self, sucursal: Sucursal) -> Sucursal:
        with self._session_factory() as session:
            modelo = self._a_modelo(sucursal)
            session.add(modelo)
            session.commit()
        return sucursal

    def actualizar(self, sucursal: Sucursal) -> Sucursal:
        with self._session_factory() as session:
            modelo = session.get(SucursalModel, sucursal.id)
            if modelo is None:
                raise ValueError(f"Sucursal {sucursal.id} no existe, no se puede actualizar")
            modelo.nombre = sucursal.nombre
            modelo.tipo = sucursal.tipo.value
            modelo.ciudad = sucursal.ciudad
            modelo.direccion = sucursal.direccion
            modelo.activa = sucursal.activa
            session.commit()
        return sucursal

    def listar(
        self,
        offset: int,
        limit: int,
        tipo: TipoSucursal | None = None,
        ciudad: str | None = None,
        activa: bool | None = None,
    ) -> tuple[list[Sucursal], int]:
        with self._session_factory() as session:
            filtros = []
            if tipo is not None:
                filtros.append(SucursalModel.tipo == tipo.value)
            if ciudad is not None:
                filtros.append(func.lower(SucursalModel.ciudad) == ciudad.strip().lower())
            if activa is not None:
                filtros.append(SucursalModel.activa == activa)

            total = session.scalar(
                select(func.count()).select_from(SucursalModel).where(*filtros)
            )

            stmt = (
                select(SucursalModel)
                .where(*filtros)
                .order_by(SucursalModel.creado_en.desc())
                .offset(offset)
                .limit(limit)
            )
            modelos = session.scalars(stmt).all()
            return [self._a_entidad(m) for m in modelos], total or 0
