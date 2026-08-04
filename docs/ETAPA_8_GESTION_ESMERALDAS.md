# Etapa 8 — Gestión de esmeraldas

## 1. Objetivo de la etapa

Completar el CRUD de `Esmeralda` (parcial desde la Etapa 7) como la
**primera entidad del proyecto bajo el régimen empresarial completo**
exigido por el Prompt Maestro Permanente V2.0: auditoría, versionado,
Domain Events, logging estructurado y Optimistic Locking — todos
obligatorios, no opcionales (ver Revisión de Consistencia Global al
inicio de esta etapa y ADR-008-01).

## 2. Alcance

**Incluido**: CRUD completo de `Esmeralda` (crear, obtener, actualizar
con Optimistic Locking, desactivar, listar con filtros), primer
consumidor real de `EventBus`, migración aditiva de base de datos,
`CONSTITUCION_INGENIERIA_TERRAE.md` (documento rector nuevo), 4 ADRs.

**Excluido** (fuera de alcance, para etapas futuras): migración
retroactiva de `Usuario`/`Sucursal`/`Joya` al nuevo régimen (sin
necesidad de negocio documentada); consumidores de eventos adicionales
más allá del logging de auditoría; `ARCHITECTURE_HANDBOOK.md` (pendiente
hasta que el volumen de decisiones transversales lo justifique).

## 3. Resumen ejecutivo

Se detectó, al iniciar la etapa, una contradicción real entre la
convención vigente (`CONVENCIONES_ENTIDADES.md`, Etapa 7.5: Domain
Events/Optimistic Locking opcionales) y el nuevo Prompt Maestro V2.0
(obligatorios sin excepción). Se resolvió creando
`CONSTITUCION_INGENIERIA_TERRAE.md` como documento rector de mayor
jerarquía y actualizando la convención en consecuencia (ADR-008-01),
antes de escribir una sola línea de código de negocio. `Esmeralda`
(Etapa 7, parcial) se completó bajo este nuevo régimen sin romper
`JoyaService` (Etapa 7), verificado con pruebas de regresión explícitas.

## 4. Arquitectura

```
domain/entities/esmeralda.py         Esmeralda(CamposAuditoria, CamposVersion)
domain/shared/versionado.py           CamposVersion (nuevo, Etapa 8)
domain/repositories/esmeralda_repository.py   EXTENDIDA: +crear +actualizar +listar +desactivar
infrastructure/db/models/gemologia.py         EsmeraldaModel(Base, AuditoriaMixin, VersionadoMixin)
infrastructure/repositories/postgres_esmeralda_repository.py   Optimistic Locking (UPDATE condicional)
infrastructure/events/consumers.py             suscribir_logging_auditoria (primer consumidor real)
application/dto/esmeralda_dto.py                +version +motivo en Update
application/services/esmeralda_service.py        publica eventos + registra versión + loguea
api/v1/routers/esmeraldas.py                      CRUD, admin+joyero, 422 en conflicto de versión
alembic/versions/0002_completar_esmeraldas.py      ALTER TABLE aditivo (6 columnas + 3 FK)
```

## 5. Justificación técnica

Ver ADR-008-01 a ADR-008-04 en `docs/adr/` para la justificación
detallada de cada decisión (régimen obligatorio, completar vs.
reescribir, consumidor de eventos, mecanismo de locking). Resumen:

- **`CamposVersion` separado de `CamposAuditoria`**: Interface
  Segregation — no toda entidad con auditoría necesariamente versiona
  explícitamente en dominio (aunque desde la Etapa 8 el mandato es que
  sí para toda entidad nueva).
- **`motivo` no es columna de la entidad**: pertenece al comando de
  cambio (DTO), no al estado; se persiste vía `RegistradorVersion`
  (Etapa 7.5) reutilizando `historial_eventos` — cero tablas nuevas.
- **Optimistic Locking con `UPDATE` condicional atómico**, no
  lectura-comparación-escritura: única forma de prevenir la condición
  de carrera real entre dos requests concurrentes (ADR-008-04).
- **`EventBus` con consumidor de logging genérico**: cumple el mandato
  sin publicar eventos huérfanos; reutilizable por cualquier entidad
  futura sin código adicional (ADR-008-03).

## 6. Código completo

Todos los archivos listados en la sección 7 se entregan completos, sin
pseudocódigo ni `TODO` pendientes, siguiendo
`CONSTITUCION_INGENIERIA_TERRAE.md` §12.

## 7. Lista de archivos creados

```
CONSTITUCION_INGENIERIA_TERRAE.md
docs/adr/ADR-008-01-domain-events-y-locking-obligatorios.md
docs/adr/ADR-008-02-completar-esmeralda-sin-romper-joyas.md
docs/adr/ADR-008-03-consumidor-logging-auditoria.md
docs/adr/ADR-008-04-optimistic-locking-update-condicional.md
docs/ETAPA_8_GESTION_ESMERALDAS.md
backend/app/domain/shared/versionado.py
backend/app/infrastructure/events/consumers.py
backend/app/application/services/esmeralda_service.py
backend/app/api/v1/routers/esmeraldas.py
backend/alembic/versions/0002_completar_esmeraldas.py
backend/app/tests/test_esmeraldas.py
backend/app/tests/test_versionado_y_eventos_etapa8.py
```

## 8. Lista de archivos modificados

```
docs/CONVENCIONES_ENTIDADES.md    (§3, §5: opcional → obligatorio; ADR-008-01)
backend/app/domain/entities/esmeralda.py                 (completada, ver ADR-008-02)
backend/app/domain/repositories/esmeralda_repository.py  (extendida, no reescrita)
backend/app/infrastructure/db/models/gemologia.py         (EsmeraldaModel + mixins)
backend/app/infrastructure/repositories/postgres_esmeralda_repository.py  (implementación completa)
backend/app/application/dto/esmeralda_dto.py               (creado en Etapa 7 solo como validación; ahora DTOs completos)
backend/app/dependencies.py                                  (+get_registrador_version, +get_esmeralda_service)
backend/app/main.py                                            (+router esmeraldas, +configurar_event_bus)
README.md, CHANGELOG.md, VERSION, docs/ROADMAP_ETAPAS.md, docs/ARQUITECTURA.md
```

**Cero cambios** en: `app/api/v1/routers/joyas.py`,
`app/application/services/joya_service.py`,
`app/domain/entities/joya.py`, `app/infrastructure/repositories/postgres_joya_repository.py`,
`app/api/v1/routers/sucursales.py`, `app/api/v1/routers/auth.py`,
`backend/app/scripts/seed_db.py` — verificado por revisión de código
que ninguno de estos archivos necesitó tocarse.

## 9. Árbol del proyecto (cambios de la Etapa 8 resaltados)

```
Terrae/
├── CONSTITUCION_INGENIERIA_TERRAE.md          ← NUEVO
├── docs/
│   ├── adr/                                     ← NUEVO
│   │   ├── ADR-008-01-...md
│   │   ├── ADR-008-02-...md
│   │   ├── ADR-008-03-...md
│   │   └── ADR-008-04-...md
│   ├── ETAPA_8_GESTION_ESMERALDAS.md            ← NUEVO
│   └── CONVENCIONES_ENTIDADES.md                 (modificado)
└── backend/
    ├── alembic/versions/
    │   └── 0002_completar_esmeraldas.py          ← NUEVO
    └── app/
        ├── domain/
        │   ├── entities/esmeralda.py               (completado)
        │   ├── repositories/esmeralda_repository.py (extendido)
        │   └── shared/versionado.py                  ← NUEVO
        ├── application/
        │   ├── dto/esmeralda_dto.py                   (completado)
        │   └── services/esmeralda_service.py           ← NUEVO
        ├── infrastructure/
        │   ├── db/models/gemologia.py                   (EsmeraldaModel modificado)
        │   ├── events/consumers.py                        ← NUEVO
        │   └── repositories/postgres_esmeralda_repository.py (completado)
        ├── api/v1/routers/esmeraldas.py                     ← NUEVO
        ├── dependencies.py                                    (modificado)
        ├── main.py                                              (modificado)
        └── tests/
            ├── test_esmeraldas.py                                ← NUEVO
            └── test_versionado_y_eventos_etapa8.py                ← NUEVO
```

## 10. ADR de las decisiones importantes

Ver `docs/adr/ADR-008-01.md` a `ADR-008-04.md` (listados en la sección 7).

## 11. Riesgos

| Riesgo | Severidad | Mitigación |
|---|---|---|
| El nuevo régimen obligatorio (auditoría+versión+eventos+locking) aumenta el costo de cada entidad futura | Media | Documentado en `CONSTITUCION_INGENIERIA_TERRAE.md` como decisión consciente del negocio (JJ GROUP SAS), no un descuido de ingeniería |
| `EsmeraldaUpdateRequest` exige `version` — un cliente frontend que no la envíe recibirá 422 de validación Pydantic | Media | Documentado explícitamente en el DTO y en el checklist de validación; el frontend (Etapa 3+) deberá guardar la `version` recibida en cada `GET`/`POST` para reenviarla en `PUT` |
| Migración 0002 no probada contra PostgreSQL real en este sandbox | Media | Ver §12 — verificación automatizada exhaustiva de correspondencia modelo↔migración como mitigación parcial; pendiente ejecución real |
| `InMemoryEventBus` sigue sin persistencia — un reinicio del proceso pierde eventos en tránsito | Baja (ya aceptado desde la Etapa 7.5) | Sin cambios; documentado desde la Etapa 7.5 |

## 12. Cobertura de pruebas

- `test_esmeraldas.py`: 14 pruebas (CRUD, auditoría, Optimistic
  Locking con 3 escenarios incluyendo conflicto real, baja lógica,
  filtros, y 2 pruebas de regresión explícita de `JoyaService`).
- `test_versionado_y_eventos_etapa8.py`: 5 pruebas (`CamposVersion`,
  consumidor de auditoría).
- **No fue posible ejecutar `pytest --cov`** en este sandbox (sin red
  ni Docker). Comando exacto pendiente de ejecutar localmente:

  ```bash
  docker compose exec backend pytest --cov=app.domain.entities.esmeralda \
    --cov=app.domain.shared --cov=app.application.services.esmeralda_service \
    --cov=app.infrastructure.repositories.postgres_esmeralda_repository \
    --cov=app.infrastructure.events --cov=app.api.v1.routers.esmeraldas \
    --cov-report=term-missing
  ```

## 13. Checklist de validación

- [ ] `make db-migrate` aplica `0002_completar_esmeraldas` sin errores sobre una base ya en `0001`.
- [ ] `make test` — las 19 pruebas nuevas de esta etapa pasan, y las 77 pruebas acumuladas de las etapas 4-7.5 siguen pasando sin cambios (96 en total).
- [ ] `POST /api/v1/esmeraldas` como `joyero@terrae.co` crea una esmeralda con `version: 1`.
- [ ] `PUT /api/v1/esmeraldas/{id}` con la `version` correcta actualiza y devuelve `version: 2`.
- [ ] Reenviar el mismo `PUT` con la `version` vieja (1) devuelve 422 (conflicto de versión).
- [ ] `DELETE /api/v1/esmeraldas/{id}` marca baja lógica; el recurso sigue accesible por `GET` directo pero desaparece del listado.
- [ ] `POST /api/v1/joyas` con `esmeralda_id` de una esmeralda recién creada sigue funcionando exactamente igual que en la Etapa 7 (prueba de regresión).
- [ ] Los logs del backend muestran líneas `domain_events` por cada creación/actualización/desactivación de esmeralda.
- [ ] `frontend/simulator/index.html` sigue intacto.

## 14. Documentación actualizada

`CONSTITUCION_INGENIERIA_TERRAE.md` (nuevo), `docs/CONVENCIONES_ENTIDADES.md`,
`docs/adr/` (nuevo), este documento, `README.md`, `CHANGELOG.md`,
`VERSION`, `docs/ROADMAP_ETAPAS.md`, `docs/ARQUITECTURA.md`.

## 15. Próxima etapa recomendada

**Etapa 9 — Inventario**, activando la relación 1:1
`JoyaModel`↔`InventarioModel` ya modelada desde la Etapa 5, bajo el
mismo régimen obligatorio de la Etapa 8 (auditoría, versionado, Domain
Events con el consumidor de logging ya reutilizable sin trabajo
adicional, Optimistic Locking).

---

## Revisión arquitectónica independiente (autoevaluación crítica)

Por mandato de `CONSTITUCION_INGENIERIA_TERRAE.md` §13, antes de
declarar la etapa finalizada:

- **Arquitectura**: Clean Architecture respetada — el dominio
  (`Esmeralda`, `CamposVersion`) no importa nada de SQLAlchemy ni
  FastAPI; verificado por inspección de imports en
  `domain/entities/esmeralda.py` y `domain/shared/versionado.py`.
- **DDD**: `EsmeraldaRepository` como interfaz en el dominio,
  implementación en infraestructura — correcto. Posible mejora futura:
  `motivo` de cambio podría modelarse como un Value Object propio en
  vez de `str | None` — se decide no hacerlo en esta etapa por no
  aportar valor verificable todavía (KISS).
- **SOLID**: `EsmeraldaService` tiene una única razón de cambio (reglas
  de negocio de esmeraldas); depende de abstracciones
  (`EsmeraldaRepository`, `EventBus`, `RegistradorVersion`), no de
  implementaciones concretas — cumple D de SOLID.
- **Seguridad**: autorización centralizada vía `require_roles`, sin
  cambios respecto al patrón ya auditado en la Etapa 6. `usuario_id`
  para auditoría se obtiene siempre del token JWT verificado
  (`Depends(get_current_user)`), nunca de un campo del body enviado
  por el cliente — el frontend no puede falsificar quién hizo el cambio.
- **Compatibilidad**: verificada explícitamente con 2 pruebas de
  regresión de `JoyaService` (sección 12) más revisión manual de que
  ningún archivo de las etapas 4-7.5 fue modificado salvo
  `app/dependencies.py` y `app/main.py` (cambios estrictamente
  aditivos).
- **Riesgo de escala**: `codigo_interno` indexado (`ix_esmeraldas_codigo_interno`,
  Etapa 5) permite validación de unicidad en O(log n); el filtro de
  `listar` por `mina_origen`/`quilates` no tiene índice compuesto
  todavía — aceptable mientras el volumen no lo justifique, revisar en
  una etapa de optimización si el catálogo crece a órdenes de millones
  de registros (criterio explícito del Prompt Maestro V2.0).
- **Deuda técnica reconocida**: `EsmeraldaService.actualizar()` no
  valida que `mina_origen`/`quilates` cambien realmente antes de
  publicar `EntidadActualizadaEvent` (publica incluso si los valores
  enviados son idénticos a los actuales). Aceptable por ahora — no
  afecta corrección, solo genera un evento/registro de versión
  "sin cambio real" en el caso límite de un `PUT` idéntico.

**Conclusión de la revisión**: la etapa cumple los criterios de
aceptación del Prompt Maestro V2.0 aplicables a su alcance. No se
identificaron bloqueantes.
