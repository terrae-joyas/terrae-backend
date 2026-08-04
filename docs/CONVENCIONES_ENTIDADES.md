# Convenciones para entidades nuevas (obligatorio desde la Etapa 8)

> **Actualizado en la Etapa 8** — el Prompt Maestro Permanente V2.0
> establece que Domain Events y Optimistic Locking dejan de ser
> opcionales: son **obligatorios para toda entidad nueva** desde esta
> etapa. Ver `CONSTITUCION_INGENIERIA_TERRAE.md` §4 (documento rector,
> prevalece sobre este) y `docs/adr/ADR-008-01-domain-events-y-locking-obligatorios.md`.
> Las secciones 3 y 5 de este documento se actualizan en consecuencia.

> Este documento nace en la Etapa 7.5 junto con la infraestructura
> transversal que describe. Aplica a **toda entidad de dominio nueva**
> a partir de la Etapa 8. Las entidades existentes (`Usuario`,
> `Sucursal`, `Joya`) no se migran retroactivamente — ver
> justificación en `docs/ETAPA_7_5_ARQUITECTURA_EMPRESARIAL.md`.
> `Esmeralda` (parcial desde la Etapa 7) se completa en la Etapa 8 bajo
> el nuevo régimen obligatorio — ver `docs/ETAPA_8_GESTION_ESMERALDAS.md`.

## 1. Auditoría

Toda entidad de dominio nueva debe heredar de `CamposAuditoria`
(`app/domain/shared/auditoria.py`) usando `@dataclass(kw_only=True)`:

```python
from dataclasses import dataclass
from app.domain.shared.auditoria import CamposAuditoria

@dataclass(kw_only=True)
class Esmeralda(CamposAuditoria):
    codigo_interno: str
    mina_origen: MinaOrigen
    # ...
```

Su modelo ORM correspondiente debe incluir `AuditoriaMixin`
(`app/infrastructure/db/mixins.py`):

```python
class EsmeraldaModel(Base, AuditoriaMixin):
    __tablename__ = "esmeraldas"
    # ...
```

El repositorio (`PostgresXxxRepository`) es responsable de completar
`creado_por`/`actualizado_por` a partir del usuario autenticado que
ejecuta la operación (pasado por el servicio de aplicación, que a su
vez lo recibe del router vía `Depends(get_current_user)`).

## 2. Baja lógica vs. máquina de estados

- Si la entidad tiene un ciclo de vida simple (activo/inactivo, como
  `Sucursal`): usar `eliminado_en`/`eliminado_por` de `CamposAuditoria`.
- Si la entidad tiene un ciclo de vida con estados intermedios con
  significado de negocio (como `Joya`): modelar una máquina de estados
  propia (ver `Joya.puede_transicionar_a()` como referencia) — **no**
  mezclar ambos mecanismos en la misma entidad.

## 3. Domain Events (obligatorio desde la Etapa 8)

Toda entidad nueva **debe** publicar al menos `EntidadCreadaEvent` y
`EntidadActualizadaEvent` vía `EventBus` (`app/infrastructure/events/event_bus.py`)
al crear/actualizar, y `EntidadDesactivadaEvent` si tiene baja lógica:

```python
from app.domain.shared.events import EntidadCreadaEvent

def crear(self, datos: ...) -> ...:
    entidad = ...
    self._repo.crear(entidad)
    self._event_bus.publicar(
        EntidadCreadaEvent(entidad_tipo="Esmeralda", entidad_id=entidad.id, datos={...})
    )
    return self._a_response(entidad)
```

**Condición obligatoria que acompaña este mandato**: la misma etapa que
introduce la publicación debe registrar al menos un consumidor real
(ver `CONSTITUCION_INGENIERIA_TERRAE.md` §6) — nunca "publicar por
publicar". El consumidor mínimo de referencia es un suscriptor de
logging de auditoría (ver `app/infrastructure/events/consumers.py`,
Etapa 8), que cualquier entidad nueva puede reutilizar sin registrar
uno propio.

## 4. Logging

Usar `get_logger(__name__)` (`app/infrastructure/logging/structured_logger.py`)
para eventos de negocio relevantes que ameriten quedar fuera del log de
requests HTTP automático (ej. una regla de negocio compleja que se
disparó, una integración externa que falló). No es necesario loguear
cada operación CRUD trivial — el `RequestLoggingMiddleware` ya cubre
el nivel HTTP de forma automática y transversal.

## 5. Concurrencia optimista (obligatorio desde la Etapa 8)

Toda entidad nueva **debe** incluir `VersionadoMixin` en su modelo ORM,
incluir `version` en el DTO de actualización, y el repositorio debe
ejecutar un `UPDATE` condicional
(`WHERE id = :id AND version = :version_esperada`), llamando a
`verificar_version()` (`app/application/concurrencia.py`) o levantando
`ConflictoDeVersionError` directamente si el `UPDATE` afecta 0 filas.


## 6. Testing

Toda pieza de infraestructura transversal nueva (mixins, eventos,
logging, concurrencia) debe tener pruebas unitarias propias,
independientes de PostgreSQL cuando sea posible (SQLite en memoria para
lo que toca base de datos, sin motor externo para lo que es lógica
pura). Todo servicio de dominio nuevo sigue el patrón ya establecido:
pruebas de integración vía `TestClient` cubriendo casos de éxito, casos
de error de negocio (400/404/409/422) y casos de autorización
(401/403).

## 7. Errores

Usar siempre las excepciones genéricas de `app/application/errors.py`
(`EntidadNoEncontradaError`, `EntidadDuplicadaError`,
`OperacionNoPermitidaError`, `ValidacionNegocioError`,
`ConflictoDeVersionError`) en vez de `HTTPException` directamente en
servicios de dominio. Los manejadores centralizados
(`app/api/v1/error_handlers.py`) ya las traducen a códigos HTTP
consistentes.

## 8. Estructura de archivos por entidad

Replicar exactamente la estructura de `sucursales`/`joyas`:

```
domain/entities/<entidad>.py
domain/repositories/<entidad>_repository.py
infrastructure/repositories/postgres_<entidad>_repository.py
application/dto/<entidad>_dto.py
application/services/<entidad>_service.py
api/v1/routers/<entidad>s.py
tests/test_<entidad>s.py
```

Wiring de DI en `app/dependencies.py`, montaje del router en
`app/main.py`, documentación de la etapa en
`docs/ETAPA_<N>_<NOMBRE>.md`.
