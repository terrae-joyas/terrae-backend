"""Implementación PostgreSQL del repositorio de inventario (Etapa 9).

`ajustar_cantidad` implementa ADR-009-01 (UPDATE condicional atómico
basado en delta, nunca sobrescritura directa de `cantidad`).
`mover` implementa Optimistic Locking estándar (ADR-008-04) para
sucursal/ubicación física.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, sessionmaker

from app.application.concurrencia import ConflictoDeVersionError
from app.application.errors import ValidacionNegocioError
from app.domain.entities.inventario import Inventario
from app.domain.repositories.inventario_repository import InventarioRepository
from app.infrastructure.db.models.gemologia import InventarioModel


class PostgresInventarioRepository(InventarioRepository):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    @staticmethod
    def _a_entidad(modelo: InventarioModel) -> Inventario:
        return Inventario(
            id=modelo.id,
            joya_id=modelo.joya_id,
            sucursal_id=modelo.sucursal_id,
            cantidad=modelo.cantidad,
            ubicacion_fisica=modelo.ubicacion_fisica,
            creado_en=modelo.creado_en,
            actualizado_en=modelo.actualizado_en,
            creado_por=modelo.creado_por,
            actualizado_por=modelo.actualizado_por,
            eliminado_en=modelo.eliminado_en,
            eliminado_por=modelo.eliminado_por,
            version=modelo.version,
        )

    def obtener_por_id(self, inventario_id: str) -> Inventario | None:
        with self._session_factory() as session:
            modelo = session.get(InventarioModel, inventario_id)
            return self._a_entidad(modelo) if modelo else None

    def obtener_por_joya_id(self, joya_id: str) -> Inventario | None:
        with self._session_factory() as session:
            modelo = (
                session.query(InventarioModel).filter(InventarioModel.joya_id == joya_id).one_or_none()
            )
            return self._a_entidad(modelo) if modelo else None

    def crear(self, inventario: Inventario, usuario_id: str | None) -> Inventario:
        with self._session_factory() as session:
            modelo = InventarioModel(
                id=inventario.id,
                joya_id=inventario.joya_id,
                sucursal_id=inventario.sucursal_id,
                cantidad=inventario.cantidad,
                ubicacion_fisica=inventario.ubicacion_fisica,
                creado_por=usuario_id,
                version=1,
                # creado_en/actualizado_en: ver nota en
                # PostgresEsmeraldaRepository.crear (Etapa 8) — se
                # dejan sin fijar para que server_default los complete.
            )
            session.add(modelo)
            session.commit()
            session.refresh(modelo)
            return self._a_entidad(modelo)

    def mover(
        self,
        inventario_id: str,
        sucursal_id: str,
        ubicacion_fisica: str | None,
        version_esperada: int,
        usuario_id: str | None,
    ) -> Inventario:
        with self._session_factory() as session:
            resultado = session.execute(
                update(InventarioModel)
                .where(InventarioModel.id == inventario_id, InventarioModel.version == version_esperada)
                .values(
                    sucursal_id=sucursal_id,
                    ubicacion_fisica=ubicacion_fisica,
                    actualizado_por=usuario_id,
                    actualizado_en=datetime.now(timezone.utc),
                    version=InventarioModel.version + 1,
                )
            )
            if resultado.rowcount == 0:
                session.rollback()
                self._lanzar_conflicto_version(session, inventario_id, version_esperada)
            session.commit()
            actualizado = session.get(InventarioModel, inventario_id)
            return self._a_entidad(actualizado)

    def ajustar_cantidad(
        self,
        inventario_id: str,
        delta: int,
        version_esperada: int,
        usuario_id: str | None,
    ) -> Inventario:
        with self._session_factory() as session:
            resultado = session.execute(
                update(InventarioModel)
                .where(
                    InventarioModel.id == inventario_id,
                    InventarioModel.version == version_esperada,
                    InventarioModel.cantidad + delta >= 0,
                )
                .values(
                    cantidad=InventarioModel.cantidad + delta,
                    actualizado_por=usuario_id,
                    actualizado_en=datetime.now(timezone.utc),
                    version=InventarioModel.version + 1,
                )
            )
            if resultado.rowcount == 0:
                session.rollback()
                actual = session.get(InventarioModel, inventario_id)
                if actual is None:
                    raise ConflictoDeVersionError(f"Inventario {inventario_id} ya no existe")
                if actual.version != version_esperada:
                    self._lanzar_conflicto_version(session, inventario_id, version_esperada)
                # La versión coincide: la causa es que el resultado sería negativo.
                raise ValidacionNegocioError(
                    f"El ajuste (delta={delta}) dejaría la cantidad en "
                    f"{actual.cantidad + delta}, por debajo de cero. "
                    f"Cantidad actual: {actual.cantidad}."
                )
            session.commit()
            actualizado = session.get(InventarioModel, inventario_id)
            return self._a_entidad(actualizado)

    def listar(
        self,
        offset: int,
        limit: int,
        sucursal_id: str | None = None,
        joya_id: str | None = None,
        cantidad_min: int | None = None,
    ) -> tuple[list[Inventario], int]:
        with self._session_factory() as session:
            filtros = [InventarioModel.eliminado_en.is_(None)]
            if sucursal_id is not None:
                filtros.append(InventarioModel.sucursal_id == sucursal_id)
            if joya_id is not None:
                filtros.append(InventarioModel.joya_id == joya_id)
            if cantidad_min is not None:
                filtros.append(InventarioModel.cantidad >= cantidad_min)

            total = session.scalar(select(func.count()).select_from(InventarioModel).where(*filtros))

            stmt = (
                select(InventarioModel)
                .where(*filtros)
                .order_by(InventarioModel.creado_en.desc())
                .offset(offset)
                .limit(limit)
            )
            modelos = session.scalars(stmt).all()
            return [self._a_entidad(m) for m in modelos], total or 0

    @staticmethod
    def _lanzar_conflicto_version(session: Session, inventario_id: str, version_esperada: int) -> None:
        actual = session.get(InventarioModel, inventario_id)
        version_actual = actual.version if actual else -1
        raise ConflictoDeVersionError(
            f"El inventario fue modificado por otro usuario (versión actual: "
            f"{version_actual}, versión enviada: {version_esperada}). "
            "Vuelve a cargar los datos antes de reintentar."
        )
