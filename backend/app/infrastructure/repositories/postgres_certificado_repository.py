"""Implementación PostgreSQL del repositorio de certificados (Etapa 10)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, sessionmaker

from app.application.concurrencia import ConflictoDeVersionError
from app.domain.entities.certificado import Certificado, EstadoCertificado
from app.domain.repositories.certificado_repository import CertificadoRepository
from app.infrastructure.db.models.certificacion import CertificadoModel


class PostgresCertificadoRepository(CertificadoRepository):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    @staticmethod
    def _a_entidad(modelo: CertificadoModel) -> Certificado:
        return Certificado(
            id=modelo.id,
            numero_certificado=modelo.numero_certificado,
            joya_id=modelo.joya_id,
            hash_sha256=modelo.hash_sha256,
            emitido_por=modelo.emitido_por,
            estado=EstadoCertificado(modelo.estado),
            emitido_en=modelo.emitido_en,
            actualizado_en=modelo.actualizado_en,
            actualizado_por=modelo.actualizado_por,
            eliminado_en=modelo.eliminado_en,
            eliminado_por=modelo.eliminado_por,
            version=modelo.version,
        )

    def obtener_por_id(self, certificado_id: str) -> Certificado | None:
        with self._session_factory() as session:
            modelo = session.get(CertificadoModel, certificado_id)
            return self._a_entidad(modelo) if modelo else None

    def obtener_certificado_activo_de_joya(self, joya_id: str) -> Certificado | None:
        with self._session_factory() as session:
            modelo = (
                session.query(CertificadoModel)
                .filter(
                    CertificadoModel.joya_id == joya_id,
                    CertificadoModel.estado == EstadoCertificado.EMITIDO.value,
                )
                .order_by(CertificadoModel.emitido_en.desc())
                .first()
            )
            return self._a_entidad(modelo) if modelo else None

    def crear(self, certificado: Certificado) -> Certificado:
        with self._session_factory() as session:
            modelo = CertificadoModel(
                id=certificado.id,
                numero_certificado=certificado.numero_certificado,
                joya_id=certificado.joya_id,
                hash_sha256=certificado.hash_sha256,
                emitido_por=certificado.emitido_por,
                estado=certificado.estado.value,
                emitido_en=certificado.emitido_en,
                version=1,
            )
            session.add(modelo)
            session.commit()
            session.refresh(modelo)
            return self._a_entidad(modelo)

    def cambiar_estado(
        self, certificado_id: str, nuevo_estado: EstadoCertificado, version_esperada: int, usuario_id: str | None
    ) -> Certificado:
        with self._session_factory() as session:
            resultado = session.execute(
                update(CertificadoModel)
                .where(CertificadoModel.id == certificado_id, CertificadoModel.version == version_esperada)
                .values(
                    estado=nuevo_estado.value,
                    actualizado_por=usuario_id,
                    actualizado_en=datetime.now(timezone.utc),
                    version=CertificadoModel.version + 1,
                )
            )
            if resultado.rowcount == 0:
                session.rollback()
                actual = session.get(CertificadoModel, certificado_id)
                version_actual = actual.version if actual else -1
                raise ConflictoDeVersionError(
                    f"El certificado fue modificado por otro usuario (versión actual: "
                    f"{version_actual}, versión enviada: {version_esperada})."
                )
            session.commit()
            actualizado = session.get(CertificadoModel, certificado_id)
            return self._a_entidad(actualizado)

    def listar(
        self,
        offset: int,
        limit: int,
        joya_id: str | None = None,
        estado: EstadoCertificado | None = None,
    ) -> tuple[list[Certificado], int]:
        with self._session_factory() as session:
            filtros = []
            if joya_id is not None:
                filtros.append(CertificadoModel.joya_id == joya_id)
            if estado is not None:
                filtros.append(CertificadoModel.estado == estado.value)

            total = session.scalar(select(func.count()).select_from(CertificadoModel).where(*filtros))
            stmt = (
                select(CertificadoModel)
                .where(*filtros)
                .order_by(CertificadoModel.emitido_en.desc())
                .offset(offset)
                .limit(limit)
            )
            modelos = session.scalars(stmt).all()
            return [self._a_entidad(m) for m in modelos], total or 0
