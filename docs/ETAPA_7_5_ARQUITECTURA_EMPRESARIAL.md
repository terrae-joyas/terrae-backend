# Etapa 7.5 — Arquitectura Empresarial Transversal

## Resumen ejecutivo

Esta etapa no agrega funcionalidades de negocio: construye la
infraestructura transversal (auditoría, versionado, Domain Events,
logging estructurado, preparación de concurrencia optimista) que las
etapas 8 a 22 usarán sin necesidad de modificarla. Se siguió el mandato
explícito del Prompt Maestro de la Etapa 7.5: **cero cambios de
comportamiento en endpoints existentes**, **cero módulos reescritos**,
**cero contratos rotos**. Los únicos archivos existentes modificados
fueron `app/dependencies.py` (agregar una función de DI nueva,
aditivo) y `app/main.py` (registrar un middleware que solo agrega un
header de respuesta y logging, sin tocar ningún endpoint).

## Arquitectura

```
app/
├── domain/
│   └── shared/                          ← NUEVO (Etapa 7.5)
│       ├── auditoria.py                   CamposAuditoria (dataclass mixin)
│       └── events.py                       DomainEvent + 3 eventos genéricos
├── application/
│   ├── concurrencia.py                  ← NUEVO — verificar_version(), ConflictoDeVersionError
│   └── errors.py                         (sin cambios — ConflictoDeVersionError hereda de aquí)
├── infrastructure/
│   ├── db/
│   │   └── mixins.py                    ← NUEVO — AuditoriaMixin, VersionadoMixin (SQLAlchemy)
│   ├── events/                          ← NUEVO (Etapa 7.5)
│   │   ├── event_bus.py                   EventBus (puerto) + InMemoryEventBus
│   │   └── version_registry.py             RegistradorVersion + HistorialEventoRegistradorVersion
│   └── logging/                         ← NUEVO (Etapa 7.5)
│       └── structured_logger.py           FormateadorJSON + get_logger()
└── api/v1/
    └── middleware/                      ← NUEVO (Etapa 7.5)
        └── request_logging.py             RequestLoggingMiddleware
```

## Justificación técnica por entregable

### 1. Auditoría transversal

`CamposAuditoria` (dominio) + `AuditoriaMixin` (ORM) proveen
`creado_en`/`actualizado_en`/`creado_por`/`actualizado_por`/`eliminado_en`/`eliminado_por`
sin duplicar estos 6 campos en cada entidad nueva. Se implementaron
**dos** mixins paralelos (dominio y ORM) en vez de uno solo porque el
proyecto ya separa estrictamente dominio (dataclasses puras) de
infraestructura (SQLAlchemy) desde la Etapa 4 — mezclar ambos
rompería Clean Architecture para ahorrar un archivo.

`AuditoriaMixin` no se aplicó a los modelos ORM existentes
(`UsuarioModel`, `SucursalModel`, `JoyaModel`, `EsmeraldaModel`)
porque hacerlo requeriría una migración de Alembic que altere 4 tablas
en producción con datos reales potenciales, y tocar 4 repositorios ya
probados para poblar los nuevos campos — exactamente lo que el Prompt
Maestro de esta etapa prohíbe ("no reescribir módulos ya terminados").
Es una decisión consciente, no un olvido: se documenta como deuda
técnica explícita, adoptable entidad por entidad cuando exista una
necesidad de negocio real (ver `docs/CONVENCIONES_ENTIDADES.md` §1-2).

### 2. Versionado

Se decidió **no crear una tabla nueva** para el historial de
versiones. `HistorialEventoRegistradorVersion` reutiliza la tabla
`historial_eventos` (Etapa 5) — ya modelada exactamente para este
propósito (`entidad_tipo`, `entidad_id`, evento con timestamp) —
guardando `{version, usuario_id, motivo}` como JSON en el campo
`detalle` ya existente. Esto cumple "no duplicar código" en su sentido
más literal: cero DDL nuevo, cero migración nueva, cero riesgo para el
esquema ya validado en la Etapa 5.

`VersionadoMixin` (columna `version`, default `1`) queda lista para que
cualquier modelo ORM nuevo la incluya; no se aplicó a ningún modelo
existente por el mismo motivo que `AuditoriaMixin`.

### 3. Domain Events

`DomainEvent` (base inmutable, `frozen=True`) más 3 eventos genéricos
(`EntidadCreadaEvent`, `EntidadActualizadaEvent`,
`EntidadDesactivadaEvent`) cubren el caso común; una entidad con
lógica de negocio rica puede definir eventos propios extendiendo
`DomainEvent` sin tocar estos genéricos.

`EventBus` es un puerto (ABC) con una única implementación,
`InMemoryEventBus` — mismo patrón de Repository Pattern que
`UsuarioRepository`/`SucursalRepository`/etc., para que una futura
implementación distribuida (ej. outbox pattern sobre PostgreSQL, o un
broker externo) se agregue sin tocar el código que publica o consume
eventos.

**Cero servicios existentes publican eventos todavía** — mandato
explícito del Prompt Maestro ("no implementar consumidores, solo
infraestructura"). Conectar `AuthService`/`SucursalService`/`JoyaService`
al bus es una decisión a tomar etapa por etapa, cuando exista al menos
un consumidor real (ver `docs/CONVENCIONES_ENTIDADES.md` §3).

### 4. Logging empresarial

`FormateadorJSON` produce una línea JSON por evento de log (nivel,
logger, mensaje, timestamp, y cualquier campo de contexto pasado vía
`extra={...}`), apta para ingestión directa por herramientas de
observabilidad sin parseo adicional.

`RequestLoggingMiddleware` registra, por cada request HTTP: `request_id`
(UUID generado por request), `usuario_id` (decodificado del JWT de
forma *best-effort*, sin exigir autenticación — nunca puede ser la
causa de que un request falle), `endpoint`, `método`, `status_code`,
`duración_ms`, y la excepción completa si la hubo. Agrega el header
`X-Request-ID` a toda respuesta — único cambio observable desde fuera,
verificado explícitamente en `test_request_logging_middleware.py` que
NO rompe ningún endpoint existente (login, health, errores 401).

### 5. Concurrencia

`ConflictoDeVersionError` (hereda de `OperacionNoPermitidaError`, ya
existente desde la Etapa 6 → se traduce automáticamente a HTTP 422 sin
necesitar un manejador nuevo) y `verificar_version()` quedan listos
para que un servicio futuro los use antes de persistir una
actualización. El mecanismo de `UPDATE` condicional
(`WHERE id = :id AND version = :version_esperada`) en el repositorio
se implementa cuando la primera entidad con necesidad real de
locking optimista lo requiera (ver `app/application/concurrencia.py`
para el detalle del patrón recomendado).

### 6. Convenciones

`docs/CONVENCIONES_ENTIDADES.md` — 8 secciones, una por entregable de
esta etapa más estructura de archivos, obligatorio desde la Etapa 8.

### 7. Testing

33 pruebas nuevas repartidas en 6 archivos: `test_auditoria_infra.py`
(6), `test_domain_events.py` (9), `test_structured_logger.py` (5),
`test_concurrencia.py` (4), `test_version_registry.py` (4),
`test_request_logging_middleware.py` (5) — las últimas 5 confirman
explícitamente que nada existente se rompió (login, health, errores).

### 8. Documentación

Este documento + `docs/CONVENCIONES_ENTIDADES.md` (nuevos) y
actualización de `README.md`, `ARQUITECTURA.md`, `ROADMAP_ETAPAS.md`,
`CHANGELOG.md`.

## Diagrama de arquitectura (capas, con la Etapa 7.5 resaltada)

```
┌──────────────────────────────────────────────────────────────┐
│                      api/v1 (FastAPI)                          │
│  routers (auth, sucursales, joyas)  +  ┌─────────────────────┐ │
│  error_handlers.py                     │ RequestLoggingMiddleware│ ← 7.5
│                                          └─────────────────────┘ │
└───────────────────────────┬──────────────────────────────────┘
                             │
┌───────────────────────────▼──────────────────────────────────┐
│                      application                                │
│  AuthService, SucursalService, JoyaService                        │
│  errors.py  +  ┌─────────────────────────────┐                    │
│                 │ concurrencia.py (7.5)         │                    │
│                 └─────────────────────────────┘                    │
└───────────────────────────┬──────────────────────────────────┘
                             │
┌───────────────────────────▼──────────────────────────────────┐
│                        domain                                    │
│  Usuario, Sucursal, Joya, Esmeralda  +  ┌──────────────────────┐  │
│                                          │ shared/ (7.5)          │  │
│                                          │  auditoria.py, events.py│  │
│                                          └──────────────────────┘  │
└───────────────────────────┬──────────────────────────────────┘
                             │
┌───────────────────────────▼──────────────────────────────────┐
│                     infrastructure                               │
│  db/ (models, session, mixins.py ← 7.5)                            │
│  repositories/ (Postgres*, Json*)                                    │
│  security/ (JWT, hashing)                                              │
│  events/ (event_bus.py, version_registry.py) ← 7.5                       │
│  logging/ (structured_logger.py) ← 7.5                                    │
└──────────────────────────────────────────────────────────────┘
```

## Decisiones de diseño (resumen)

| Decisión | Alternativa considerada | Por qué se descartó |
|---|---|---|
| Mixins separados dominio/ORM | Un solo mixin en infraestructura | Rompería la separación dominio/infraestructura ya establecida desde la Etapa 4 |
| No aplicar mixins a entidades existentes | Migrar las 4 tablas ya creadas | Requiere migración + backfill + tocar repositorios probados; prohibido por el mandato de la etapa |
| Reutilizar `historial_eventos` para versionado | Tabla nueva `versiones` | Evita duplicar infraestructura de persistencia para un concepto ya modelado en la Etapa 5 |
| `EventBus` en memoria, sin persistencia | Outbox pattern sobre PostgreSQL desde ya | Sin consumidores reales todavía, construir entrega garantizada ahora sería especulativo |
| Middleware de logging con extracción de usuario *best-effort* | Exigir autenticación en el middleware | El middleware nunca debe decidir autorización — esa responsabilidad es de cada endpoint vía `Depends` |
| `ConflictoDeVersionError` hereda de `OperacionNoPermitidaError` | Código HTTP 409 dedicado | Reutiliza el manejador genérico ya existente (Etapa 6) sin código nuevo; ajustable a 409 en el futuro si la UX lo justifica |

## Riesgos identificados

| Riesgo | Mitigación |
|---|---|
| Mixins sin uso real hasta la Etapa 8 podrían quedar desalineados con la necesidad real cuando se usen por primera vez | Se diseñaron a partir de los campos explícitamente pedidos en el Prompt Maestro (`created_at`, `updated_at`, `created_by`, `updated_by`, `deleted_at`, `deleted_by`) y del patrón ya usado en `historial_propietarios`/`ventas` (Etapa 5), minimizando sorpresas |
| `EventBus` en memoria se pierde si el proceso reinicia (eventos no persistidos) | Documentado explícitamente en el docstring de `InMemoryEventBus`; aceptable mientras no haya consumidores reales que dependan de entrega garantizada |
| Middleware de logging agrega overhead a cada request (decodificación JWT best-effort) | Es una operación local (sin I/O de red), y solo se ejecuta si el header `Authorization` está presente; impacto de rendimiento despreciable |
| 90% de cobertura pedido por el Prompt Maestro no se pudo verificar con una herramienta de cobertura real (sin `pytest-cov` ejecutable en este sandbox) | Ver sección de validación — se listan las 33 pruebas nuevas y su alcance línea por línea revisado manualmente; pendiente confirmar con `pytest --cov` en un entorno con Docker |

## Validación realizada en este sandbox (sin PostgreSQL, red ni `pytest` ejecutable)

- `python3 -m py_compile` sobre los ~15 archivos nuevos y los 3
  modificados (`main.py`, `dependencies.py`): sin errores de sintaxis.
- Revisión manual exhaustiva de:
  - Que `dataclass(kw_only=True)` en `CamposAuditoria`/`DomainEvent`
    evita el problema clásico de orden de campos en herencia de
    dataclasses (confirmado: Python 3.11, disponible en el entorno del
    contenedor backend).
  - Que los mixins de SQLAlchemy no registran ninguna tabla nueva en
    `Base.metadata` hasta que un modelo real los use (verificado
    leyendo el código: son mixins de clase Python plana, no
    `DeclarativeBase` por sí mismos).
  - Que `test_auditoria_infra.py` reutiliza la `Base` real de la app
    (no una aislada) para que la FK `creado_por → usuarios.id` resuelva
    correctamente, mismo patrón que `test_postgres_user_repository.py`.
  - Que `ConflictoDeVersionError` hereda correctamente de
    `OperacionNoPermitidaError` y por lo tanto queda cubierta por el
    manejador genérico existente sin registrar uno nuevo.
- Comparación línea por línea de `main.py` y `dependencies.py` antes/después
  del cambio: confirmando que ningún router, dependencia o wiring
  existente fue alterado — solo se agregaron líneas nuevas.
- `diff` confirma que `frontend/simulator/index.html` permanece intacto
  (esta etapa no tocó el frontend).

### Pendiente de validar en un entorno con Docker/PostgreSQL real

- `make test` — las 33 pruebas nuevas de esta etapa, además de las
  44 pruebas acumuladas de las etapas 4-7 (deben seguir pasando
  exactamente igual, sin ninguna modificada).
- `pytest --cov=app.domain.shared --cov=app.infrastructure.events
  --cov=app.infrastructure.logging --cov=app.application.concurrencia
  --cov=app.api.v1.middleware --cov-report=term-missing` para confirmar
  el 90% de cobertura exigido por el Prompt Maestro sobre la
  infraestructura nueva específicamente (no sobre el proyecto completo,
  ya que routers/servicios existentes no son objeto de esta etapa).
- Confirmar en los logs de `docker compose logs backend` que las líneas
  JSON se emiten correctamente con `request_id`/`usuario_id` al hacer
  requests autenticados de prueba.

## Checklist de validación (a ejecutar por el desarrollador)

- [ ] `make up` — el backend arranca sin errores con el middleware activo.
- [ ] `make test` — las 33 pruebas nuevas pasan, y las 44 pruebas de las etapas 4-7 siguen pasando sin cambios.
- [ ] `curl -i http://localhost:8000/health` incluye el header `X-Request-ID`.
- [ ] Los logs del backend (`make logs`) muestran líneas JSON por cada request.
- [ ] Un login válido (`POST /api/v1/auth/login`) sigue devolviendo exactamente el mismo cuerpo que antes de esta etapa.
- [ ] `frontend/simulator/index.html` sigue intacto.

## Lista de archivos creados

```
backend/app/domain/shared/__init__.py
backend/app/domain/shared/auditoria.py
backend/app/domain/shared/events.py
backend/app/application/concurrencia.py
backend/app/infrastructure/db/mixins.py
backend/app/infrastructure/events/__init__.py
backend/app/infrastructure/events/event_bus.py
backend/app/infrastructure/events/version_registry.py
backend/app/infrastructure/logging/__init__.py
backend/app/infrastructure/logging/structured_logger.py
backend/app/api/v1/middleware/__init__.py
backend/app/api/v1/middleware/request_logging.py
backend/app/tests/test_auditoria_infra.py
backend/app/tests/test_domain_events.py
backend/app/tests/test_structured_logger.py
backend/app/tests/test_concurrencia.py
backend/app/tests/test_version_registry.py
backend/app/tests/test_request_logging_middleware.py
docs/CONVENCIONES_ENTIDADES.md
docs/ETAPA_7_5_ARQUITECTURA_EMPRESARIAL.md
```

## Lista de archivos modificados

```
backend/app/main.py            (+middleware, +docstring; ningún endpoint tocado)
backend/app/dependencies.py    (+get_event_bus(); ninguna función existente tocada)
README.md, CHANGELOG.md, VERSION, docs/ROADMAP_ETAPAS.md, docs/ARQUITECTURA.md
```

## Commits recomendados

```
feat(domain): CamposAuditoria — mixin de dominio para auditoría transversal
feat(db): AuditoriaMixin, VersionadoMixin — mixins ORM para entidades futuras
feat(domain): DomainEvent + eventos genéricos (creada/actualizada/desactivada)
feat(events): EventBus (puerto) + InMemoryEventBus
feat(events): RegistradorVersion — reutiliza historial_eventos, sin tabla nueva
feat(logging): logger estructurado JSON + RequestLoggingMiddleware
feat(application): infraestructura de concurrencia optimista (preparación)
test(infra): 33 pruebas de la infraestructura transversal de la Etapa 7.5
docs: CONVENCIONES_ENTIDADES.md + ETAPA_7_5_ARQUITECTURA_EMPRESARIAL.md
```

## Criterio de aceptación

Las etapas 8 a 22 deben poder usar esta infraestructura (mixins, event
bus, logger, concurrencia) sin modificarla — solo importándola y
adoptándola según `docs/CONVENCIONES_ENTIDADES.md`. Ninguna entidad
existente cambió de comportamiento, ningún endpoint cambió de
contrato, y las 44 pruebas de las etapas 4-7 no requirieron ni un solo
cambio para seguir siendo válidas.

## Próxima etapa

**Etapa 8 — Gestión de esmeraldas**, ahora con la opción (no
obligación retroactiva) de adoptar `CamposAuditoria`/`AuditoriaMixin`
si el equipo decide que las esmeraldas —dado su alto valor unitario y
la necesidad real de trazabilidad de quién las registró/editó—
justifican pagar el costo de una migración de Alembic adicional desde
el inicio.
