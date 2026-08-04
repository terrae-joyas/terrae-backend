"""Implementación PostgreSQL del repositorio de joyas."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.domain.entities.joya import EstadoJoya, Joya, TipoJoya
from app.domain.repositories.joya_repository import JoyaRepository
from app.infrastructure.db.models.gemologia import JoyaModel


class PostgresJoyaRepository(JoyaRepository):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    @staticmethod
    def _a_entidad(modelo: JoyaModel) -> Joya:
        return Joya(
            id=modelo.id,
            referencia=modelo.referencia,
            nombre=modelo.nombre,
            tipo=TipoJoya(modelo.tipo),
            material_metal=modelo.material_metal,
            estado=EstadoJoya(modelo.estado),
            esmeralda_id=modelo.esmeralda_id,
            sucursal_id=modelo.sucursal_id,
            creado_en=modelo.creado_en,
        )

    @staticmethod
    def _a_modelo(joya: Joya) -> JoyaModel:
        return JoyaModel(
            id=joya.id,
            referencia=joya.referencia,
            nombre=joya.nombre,
            tipo=joya.tipo.value,
            material_metal=joya.material_metal,
            estado=joya.estado.value,
            esmeralda_id=joya.esmeralda_id,
            sucursal_id=joya.sucursal_id,
            creado_en=joya.creado_en,
        )

    def obtener_por_id(self, joya_id: str) -> Joya | None:
        with self._session_factory() as session:
            modelo = session.get(JoyaModel, joya_id)
            return self._a_entidad(modelo) if modelo else None

    def obtener_por_referencia(self, referencia: str) -> Joya | None:
        with self._session_factory() as session:
            modelo = (
                session.query(JoyaModel).filter(JoyaModel.referencia == referencia).one_or_none()
            )
            return self._a_entidad(modelo) if modelo else None

    def crear(self, joya: Joya) -> Joya:
        with self._session_factory() as session:
            modelo = self._a_modelo(joya)
            session.add(modelo)
            session.commit()
        return joya

    def actualizar(self, joya: Joya) -> Joya:
        with self._session_factory() as session:
            modelo = session.get(JoyaModel, joya.id)
            if modelo is None:
                raise ValueError(f"Joya {joya.id} no existe, no se puede actualizar")
            modelo.nombre = joya.nombre
            modelo.tipo = joya.tipo.value
            modelo.material_metal = joya.material_metal
            modelo.estado = joya.estado.value
            modelo.esmeralda_id = joya.esmeralda_id
            modelo.sucursal_id = joya.sucursal_id
            session.commit()
        return joya

    def listar(
        self,
        offset: int,
        limit: int,
        tipo: TipoJoya | None = None,
        estado: EstadoJoya | None = None,
        sucursal_id: str | None = None,
        esmeralda_id: str | None = None,
    ) -> tuple[list[Joya], int]:
        with self._session_factory() as session:
            filtros = []
            if tipo is not None:
                filtros.append(JoyaModel.tipo == tipo.value)
            if estado is not None:
                filtros.append(JoyaModel.estado == estado.value)
            if sucursal_id is not None:
                filtros.append(JoyaModel.sucursal_id == sucursal_id)
            if esmeralda_id is not None:
                filtros.append(JoyaModel.esmeralda_id == esmeralda_id)

            total = session.scalar(select(func.count()).select_from(JoyaModel).where(*filtros))

            stmt = (
                select(JoyaModel)
                .where(*filtros)
                .order_by(JoyaModel.creado_en.desc())
                .offset(offset)
                .limit(limit)
            )
            modelos = session.scalars(stmt).all()
            return [self._a_entidad(m) for m in modelos], total or 0
