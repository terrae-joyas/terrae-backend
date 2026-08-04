"""
Infraestructura de versionado (Etapa 7.5 — preparación, sin historial
completo todavía).

`RegistradorVersion` es el puerto que un servicio de aplicación futuro
usará para dejar constancia de que una entidad cambió de versión, con
quién y por qué. La única implementación de esta etapa,
`HistorialEventoRegistradorVersion`, reutiliza la tabla
`historial_eventos` ya creada en la Etapa 5 (dominio, `entidad_tipo`,
`entidad_id`, `evento`, `detalle`, `ocurrido_en`) en vez de crear una
tabla nueva — evita duplicar infraestructura de persistencia para un
concepto (registro de eventos de una entidad a lo largo del tiempo) que
ya existe. El campo `detalle` almacena un JSON con `{version, usuario,
motivo}`.

No se implementa aquí:
- Reconstrucción de una entidad a partir de su historial (event
  sourcing completo) — fuera de alcance de esta etapa.
- Aplicación automática a ninguna entidad existente — ningún servicio
  llama a esto todavía.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod

from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db.models.auditoria import HistorialEventoModel


class RegistradorVersion(ABC):
    @abstractmethod
    def registrar_version(
        self,
        entidad_tipo: str,
        entidad_id: str,
        version: int,
        usuario_id: str | None,
        motivo: str | None = None,
    ) -> None: ...


class HistorialEventoRegistradorVersion(RegistradorVersion):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def registrar_version(
        self,
        entidad_tipo: str,
        entidad_id: str,
        version: int,
        usuario_id: str | None,
        motivo: str | None = None,
    ) -> None:
        import uuid

        detalle = json.dumps(
            {"version": version, "usuario_id": usuario_id, "motivo": motivo},
            ensure_ascii=False,
        )
        with self._session_factory() as session:
            session.add(
                HistorialEventoModel(
                    id=str(uuid.uuid4()),
                    entidad_tipo=entidad_tipo,
                    entidad_id=entidad_id,
                    evento="version_registrada",
                    detalle=detalle,
                )
            )
            session.commit()
