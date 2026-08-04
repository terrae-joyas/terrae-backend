"""
Servicio de aplicación: certificados digitales (Etapa 10).

Reglas de negocio:
1. La joya debe existir.
2. Una joya no puede tener más de un certificado en estado `emitido`
   a la vez (debe revocarse el vigente antes de emitir uno nuevo).
3. `numero_certificado` se genera server-side (nunca lo decide el
   cliente — es un documento oficial). `hash_sha256` se calcula sobre
   un payload canónico (joya + número + fecha de emisión), como ancla
   de integridad para la futura verificación en blockchain (Etapa 12;
   recordar `CONSTITUCION_INGENIERIA_TERRAE.md` §7: blockchain nunca es
   la fuente de verdad, solo certifica lo que ya es correcto aquí).
4. Un certificado escaneado/generado (PDF, imagen) se asocia como
   `ActivoMultimedia` polimórfico (`entidad_tipo="Certificado"`) — sin
   acoplar este servicio a esa entidad más allá de exponer el `id`
   necesario para la asociación (ADR-010-01).
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from uuid import uuid4

from app.application.dto.certificado_dto import (
    CertificadoEmitirRequest,
    CertificadoResponse,
    CertificadoRevocarRequest,
)
from app.application.errors import (
    EntidadDuplicadaError,
    EntidadNoEncontradaError,
    OperacionNoPermitidaError,
)
from app.domain.entities.certificado import Certificado, EstadoCertificado
from app.domain.repositories.certificado_repository import CertificadoRepository
from app.domain.repositories.joya_repository import JoyaRepository
from app.domain.shared.events import EntidadCreadaEvent, EntidadDesactivadaEvent
from app.infrastructure.events.event_bus import EventBus
from app.infrastructure.events.version_registry import RegistradorVersion
from app.infrastructure.logging.structured_logger import get_logger

logger = get_logger("certificado_service")


class CertificadoService:
    def __init__(
        self,
        repositorio: CertificadoRepository,
        joya_repositorio: JoyaRepository,
        event_bus: EventBus,
        registrador_version: RegistradorVersion,
    ) -> None:
        self._repo = repositorio
        self._joyas = joya_repositorio
        self._event_bus = event_bus
        self._registrador_version = registrador_version

    def emitir(self, datos: CertificadoEmitirRequest, usuario_id: str | None) -> CertificadoResponse:
        if self._joyas.obtener_por_id(datos.joya_id) is None:
            raise EntidadNoEncontradaError(f"Joya {datos.joya_id} no encontrada")

        if self._repo.obtener_certificado_activo_de_joya(datos.joya_id) is not None:
            raise EntidadDuplicadaError(
                f"La joya {datos.joya_id} ya tiene un certificado vigente. "
                "Revócalo antes de emitir uno nuevo."
            )

        emitido_en = datetime.now(timezone.utc)
        numero_certificado = self._generar_numero_certificado(emitido_en)
        hash_sha256 = self._calcular_hash(datos.joya_id, numero_certificado, emitido_en)

        certificado = Certificado(
            numero_certificado=numero_certificado,
            joya_id=datos.joya_id,
            hash_sha256=hash_sha256,
            emitido_por=usuario_id,
            emitido_en=emitido_en,
        )
        certificado = self._repo.crear(certificado)

        logger.info(
            "Certificado emitido",
            extra={
                "certificado_id": certificado.id,
                "numero_certificado": certificado.numero_certificado,
                "joya_id": certificado.joya_id,
                "usuario_id": usuario_id,
            },
        )
        self._event_bus.publicar(
            EntidadCreadaEvent(
                entidad_tipo="Certificado",
                entidad_id=certificado.id,
                usuario_id=usuario_id,
                datos={
                    "numero_certificado": certificado.numero_certificado,
                    "joya_id": certificado.joya_id,
                    "hash_sha256": certificado.hash_sha256,
                },
            )
        )
        self._registrador_version.registrar_version(
            entidad_tipo="Certificado",
            entidad_id=certificado.id,
            version=certificado.version,
            usuario_id=usuario_id,
            motivo="Emisión inicial",
        )
        return self._a_response(certificado)

    def obtener(self, certificado_id: str) -> CertificadoResponse:
        certificado = self._obtener_o_lanzar(certificado_id)
        return self._a_response(certificado)

    def revocar(
        self, certificado_id: str, datos: CertificadoRevocarRequest, usuario_id: str | None
    ) -> CertificadoResponse:
        certificado = self._obtener_o_lanzar(certificado_id)
        if not certificado.puede_revocarse():
            raise OperacionNoPermitidaError(
                f"El certificado está en estado '{certificado.estado.value}'; solo puede "
                "revocarse un certificado en estado 'emitido'."
            )

        actualizado = self._repo.cambiar_estado(
            certificado_id, EstadoCertificado.REVOCADO, datos.version, usuario_id
        )

        logger.info(
            "Certificado revocado",
            extra={"certificado_id": certificado_id, "motivo": datos.motivo, "usuario_id": usuario_id},
        )
        self._event_bus.publicar(
            EntidadDesactivadaEvent(
                entidad_tipo="Certificado", entidad_id=certificado_id, usuario_id=usuario_id, motivo=datos.motivo
            )
        )
        self._registrador_version.registrar_version(
            entidad_tipo="Certificado",
            entidad_id=certificado_id,
            version=actualizado.version,
            usuario_id=usuario_id,
            motivo=datos.motivo,
        )
        return self._a_response(actualizado)

    def listar(
        self, offset: int, limit: int, joya_id: str | None, estado: EstadoCertificado | None
    ) -> tuple[list[CertificadoResponse], int]:
        items, total = self._repo.listar(offset, limit, joya_id, estado)
        return [self._a_response(c) for c in items], total

    # --- Helpers internos ---
    def _obtener_o_lanzar(self, certificado_id: str) -> Certificado:
        certificado = self._repo.obtener_por_id(certificado_id)
        if certificado is None:
            raise EntidadNoEncontradaError(f"Certificado {certificado_id} no encontrado")
        return certificado

    @staticmethod
    def _generar_numero_certificado(emitido_en: datetime) -> str:
        return f"CERT-{emitido_en.strftime('%Y%m')}-{uuid4().hex[:8].upper()}"

    @staticmethod
    def _calcular_hash(joya_id: str, numero_certificado: str, emitido_en: datetime) -> str:
        payload = f"{joya_id}|{numero_certificado}|{emitido_en.isoformat()}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _a_response(certificado: Certificado) -> CertificadoResponse:
        return CertificadoResponse(
            id=certificado.id,
            numero_certificado=certificado.numero_certificado,
            joya_id=certificado.joya_id,
            hash_sha256=certificado.hash_sha256,
            emitido_por=certificado.emitido_por,
            estado=certificado.estado,
            emitido_en=certificado.emitido_en,
            actualizado_en=certificado.actualizado_en,
            actualizado_por=certificado.actualizado_por,
            version=certificado.version,
        )
