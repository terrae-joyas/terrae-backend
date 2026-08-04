"""Implementación PostgreSQL del repositorio de esmeraldas.

Completada en la Etapa 8 (ver ADR-008-02, ADR-008-04). El método
`actualizar` implementa Optimistic Locking mediante un `UPDATE`
condicional atómico — nunca lectura-comparación-escritura en dos pasos.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, sessionmaker

from app.application.concurrencia import ConflictoDeVersionError
from app.domain.entities.esmeralda import Esmeralda, MinaOrigen
from app.domain.repositories.esmeralda_repository import EsmeraldaRepository
from app.infrastructure.db.models.gemologia import EsmeraldaModel, JoyaModel


class PostgresEsmeraldaRepository(EsmeraldaRepository):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    @staticmethod
    def _a_entidad(modelo: EsmeraldaModel) -> Esmeralda:
        return Esmeralda(
            id=modelo.id,
            codigo_interno=modelo.codigo_interno,
            mina_origen=MinaOrigen(modelo.mina_origen),
            quilates=modelo.quilates,
            color=modelo.color,
            claridad=modelo.claridad,
            corte=modelo.corte,
            tratamientos=modelo.tratamientos,
            tipo_inclusion_principal=modelo.tipo_inclusion_principal,
            creado_en=modelo.creado_en,
            actualizado_en=modelo.actualizado_en,
            creado_por=modelo.creado_por,
            actualizado_por=modelo.actualizado_por,
            eliminado_en=modelo.eliminado_en,
            eliminado_por=modelo.eliminado_por,
            version=modelo.version,
        )

    def obtener_por_id(self, esmeralda_id: str) -> Esmeralda | None:
        with self._session_factory() as session:
            modelo = session.get(EsmeraldaModel, esmeralda_id)
            return self._a_entidad(modelo) if modelo else None

    def obtener_por_codigo_interno(self, codigo_interno: str) -> Esmeralda | None:
        with self._session_factory() as session:
            modelo = (
                session.query(EsmeraldaModel)
                .filter(EsmeraldaModel.codigo_interno == codigo_interno)
                .one_or_none()
            )
            return self._a_entidad(modelo) if modelo else None

    def esta_vinculada_a_joya_activa(self, esmeralda_id: str, excluir_joya_id: str | None = None) -> bool:
        with self._session_factory() as session:
            stmt = select(JoyaModel.id).where(
                JoyaModel.esmeralda_id == esmeralda_id,
                JoyaModel.estado != "dada_de_baja",
            )
            if excluir_joya_id is not None:
                stmt = stmt.where(JoyaModel.id != excluir_joya_id)
            return session.scalar(stmt) is not None

    def crear(self, esmeralda: Esmeralda, usuario_id: str | None) -> Esmeralda:
        with self._session_factory() as session:
            modelo = EsmeraldaModel(
                id=esmeralda.id,
                codigo_interno=esmeralda.codigo_interno,
                mina_origen=esmeralda.mina_origen.value,
                quilates=esmeralda.quilates,
                color=esmeralda.color,
                claridad=esmeralda.claridad,
                corte=esmeralda.corte,
                tratamientos=esmeralda.tratamientos,
                tipo_inclusion_principal=esmeralda.tipo_inclusion_principal,
                creado_por=usuario_id,
                version=1,
                # creado_en/actualizado_en NO se fijan aquí a propósito:
                # se deja que server_default=func.now() de AuditoriaMixin
                # los complete. Fijarlos explícitamente a None insertaría
                # NULL y violaría la restricción NOT NULL de la columna.
            )
            session.add(modelo)
            session.commit()
            session.refresh(modelo)
            return self._a_entidad(modelo)

    def actualizar(self, esmeralda: Esmeralda, version_esperada: int, usuario_id: str | None) -> Esmeralda:
        with self._session_factory() as session:
            resultado = session.execute(
                update(EsmeraldaModel)
                .where(EsmeraldaModel.id == esmeralda.id, EsmeraldaModel.version == version_esperada)
                .values(
                    mina_origen=esmeralda.mina_origen.value,
                    quilates=esmeralda.quilates,
                    color=esmeralda.color,
                    claridad=esmeralda.claridad,
                    corte=esmeralda.corte,
                    tratamientos=esmeralda.tratamientos,
                    tipo_inclusion_principal=esmeralda.tipo_inclusion_principal,
                    actualizado_por=usuario_id,
                    actualizado_en=datetime.now(timezone.utc),
                    version=EsmeraldaModel.version + 1,
                )
            )
            if resultado.rowcount == 0:
                session.rollback()
                actual = session.get(EsmeraldaModel, esmeralda.id)
                version_actual = actual.version if actual else -1
                raise ConflictoDeVersionError(
                    f"La esmeralda fue modificada por otro usuario (versión actual: "
                    f"{version_actual}, versión enviada: {version_esperada}). "
                    "Vuelve a cargar los datos antes de reintentar."
                )
            session.commit()
            actualizado = session.get(EsmeraldaModel, esmeralda.id)
            return self._a_entidad(actualizado)

    def desactivar(self, esmeralda_id: str, usuario_id: str | None) -> Esmeralda:
        with self._session_factory() as session:
            modelo = session.get(EsmeraldaModel, esmeralda_id)
            if modelo is None:
                raise ValueError(f"Esmeralda {esmeralda_id} no existe, no se puede desactivar")
            modelo.eliminado_en = datetime.now(timezone.utc)
            modelo.eliminado_por = usuario_id
            modelo.version = modelo.version + 1
            session.commit()
            session.refresh(modelo)
            return self._a_entidad(modelo)

    def listar(
        self,
        offset: int,
        limit: int,
        mina_origen: MinaOrigen | None = None,
        quilates_min: float | None = None,
        quilates_max: float | None = None,
    ) -> tuple[list[Esmeralda], int]:
        with self._session_factory() as session:
            filtros = [EsmeraldaModel.eliminado_en.is_(None)]
            if mina_origen is not None:
                filtros.append(EsmeraldaModel.mina_origen == mina_origen.value)
            if quilates_min is not None:
                filtros.append(EsmeraldaModel.quilates >= quilates_min)
            if quilates_max is not None:
                filtros.append(EsmeraldaModel.quilates <= quilates_max)

            total = session.scalar(select(func.count()).select_from(EsmeraldaModel).where(*filtros))

            stmt = (
                select(EsmeraldaModel)
                .where(*filtros)
                .order_by(EsmeraldaModel.creado_en.desc())
                .offset(offset)
                .limit(limit)
            )
            modelos = session.scalars(stmt).all()
            return [self._a_entidad(m) for m in modelos], total or 0
