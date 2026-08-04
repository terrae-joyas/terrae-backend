"""Interfaz del repositorio de certificados (Etapa 10)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.certificado import Certificado, EstadoCertificado


class CertificadoRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, certificado_id: str) -> Certificado | None: ...

    @abstractmethod
    def obtener_certificado_activo_de_joya(self, joya_id: str) -> Certificado | None:
        """El certificado en estado `emitido` más reciente de la joya,
        si existe (una joya puede tener certificados `revocado`
        históricos, pero como máximo uno `emitido` a la vez)."""
        ...

    @abstractmethod
    def crear(self, certificado: Certificado) -> Certificado: ...

    @abstractmethod
    def cambiar_estado(
        self, certificado_id: str, nuevo_estado: EstadoCertificado, version_esperada: int, usuario_id: str | None
    ) -> Certificado:
        """Optimistic Locking estándar (ADR-008-04)."""
        ...

    @abstractmethod
    def listar(
        self,
        offset: int,
        limit: int,
        joya_id: str | None = None,
        estado: EstadoCertificado | None = None,
    ) -> tuple[list[Certificado], int]:
        """Devuelve (elementos_de_la_pagina, total_que_cumple_el_filtro)."""
        ...
