"""Interfaz del repositorio de esmeraldas.

Contrato parcial en la Etapa 7 a propósito: solo se necesitaba
`obtener_por_id` (validar que una esmeralda existe al vincularla a una
joya) y `esta_vinculada_a_joya_activa` (regla de negocio: una esmeralda
no puede estar en dos joyas activas a la vez). La Etapa 8 EXTIENDE esta
misma interfaz con `crear`, `actualizar` (con Optimistic Locking,
ver ADR-008-04) y `listar` — no se duplica ni se reescribe, solo se
completa (ver ADR-008-02).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.esmeralda import Esmeralda, MinaOrigen


class EsmeraldaRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, esmeralda_id: str) -> Esmeralda | None: ...

    @abstractmethod
    def esta_vinculada_a_joya_activa(self, esmeralda_id: str, excluir_joya_id: str | None = None) -> bool:
        """True si la esmeralda ya está asociada a una joya que no esté
        `dada_de_baja`. `excluir_joya_id` permite validar una
        actualización sin que la propia joya se cuente a sí misma."""
        ...

    @abstractmethod
    def obtener_por_codigo_interno(self, codigo_interno: str) -> Esmeralda | None: ...

    @abstractmethod
    def crear(self, esmeralda: Esmeralda, usuario_id: str | None) -> Esmeralda: ...

    @abstractmethod
    def actualizar(self, esmeralda: Esmeralda, version_esperada: int, usuario_id: str | None) -> Esmeralda:
        """Actualiza de forma atómica solo si `version_esperada` coincide
        con la versión actual en base de datos (Optimistic Locking, ver
        ADR-008-04). Levanta `ConflictoDeVersionError` si no coincide."""
        ...

    @abstractmethod
    def desactivar(self, esmeralda_id: str, usuario_id: str | None) -> Esmeralda:
        """Baja lógica (`eliminado_en`/`eliminado_por`) — ver
        docs/CONVENCIONES_ENTIDADES.md §2. Esmeralda no tiene máquina de
        estados propia (a diferencia de Joya), por lo que usa el
        mecanismo genérico de `CamposAuditoria`."""
        ...

    @abstractmethod
    def listar(
        self,
        offset: int,
        limit: int,
        mina_origen: MinaOrigen | None = None,
        quilates_min: float | None = None,
        quilates_max: float | None = None,
    ) -> tuple[list[Esmeralda], int]:
        """Devuelve (elementos_de_la_pagina, total_que_cumple_el_filtro)."""
        ...
