"""Implementación PostgreSQL del repositorio de activos multimedia (Etapa 10)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.domain.entities.activo_multimedia import ActivoMultimedia, TipoActivoMultimedia
from app.domain.repositories.activo_multimedia_repository import ActivoMultimediaRepository
from app.infrastructure.db.models.multimedia import ActivoMultimediaModel


class PostgresActivoMultimediaRepository(ActivoMultimediaRepository):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    @staticmethod
    def _a_entidad(modelo: ActivoMultimediaModel) -> ActivoMultimedia:
        return ActivoMultimedia(
            id=modelo.id,
            entidad_tipo=modelo.entidad_tipo,
            entidad_id=modelo.entidad_id,
            tipo=TipoActivoMultimedia(modelo.tipo),
            url=modelo.url,
            hash_sha256=modelo.hash_sha256,
            dispositivo=modelo.dispositivo,
            creado_en=modelo.creado_en,
            actualizado_en=modelo.actualizado_en,
            creado_por=modelo.creado_por,
            actualizado_por=modelo.actualizado_por,
            eliminado_en=modelo.eliminado_en,
            eliminado_por=modelo.eliminado_por,
            version=modelo.version,
        )

    def obtener_por_id(self, activo_id: str) -> ActivoMultimedia | None:
        with self._session_factory() as session:
            modelo = session.get(ActivoMultimediaModel, activo_id)
            return self._a_entidad(modelo) if modelo else None

    def crear(self, activo: ActivoMultimedia, usuario_id: str | None) -> ActivoMultimedia:
        with self._session_factory() as session:
            modelo = ActivoMultimediaModel(
                id=activo.id,
                entidad_tipo=activo.entidad_tipo,
                entidad_id=activo.entidad_id,
                tipo=activo.tipo.value,
                url=activo.url,
                hash_sha256=activo.hash_sha256,
                dispositivo=activo.dispositivo,
                creado_por=usuario_id,
                version=1,
            )
            session.add(modelo)
            session.commit()
            session.refresh(modelo)
            return self._a_entidad(modelo)

    def desactivar(self, activo_id: str, usuario_id: str | None) -> ActivoMultimedia:
        with self._session_factory() as session:
            modelo = session.get(ActivoMultimediaModel, activo_id)
            if modelo is None:
                raise ValueError(f"Activo multimedia {activo_id} no existe, no se puede desactivar")
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
        entidad_tipo: str | None = None,
        entidad_id: str | None = None,
        tipo: TipoActivoMultimedia | None = None,
    ) -> tuple[list[ActivoMultimedia], int]:
        with self._session_factory() as session:
            filtros = [ActivoMultimediaModel.eliminado_en.is_(None)]
            if entidad_tipo is not None:
                filtros.append(ActivoMultimediaModel.entidad_tipo == entidad_tipo)
            if entidad_id is not None:
                filtros.append(ActivoMultimediaModel.entidad_id == entidad_id)
            if tipo is not None:
                filtros.append(ActivoMultimediaModel.tipo == tipo.value)

            total = session.scalar(
                select(func.count()).select_from(ActivoMultimediaModel).where(*filtros)
            )
            stmt = (
                select(ActivoMultimediaModel)
                .where(*filtros)
                .order_by(ActivoMultimediaModel.creado_en.desc())
                .offset(offset)
                .limit(limit)
            )
            modelos = session.scalars(stmt).all()
            return [self._a_entidad(m) for m in modelos], total or 0
