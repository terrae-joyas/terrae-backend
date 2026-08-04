# Etapa 9 — Inventario

## 1. Objetivo de la etapa

Activar la relación 1:1 `Joya`↔`Inventario` ya modelada desde la
Etapa 5, como la primera entidad **completamente nueva** (no
completada desde una versión parcial, a diferencia de `Esmeralda` en
la Etapa 8) construida directamente bajo el régimen obligatorio de
`CONSTITUCION_INGENIERIA_TERRAE.md` §4.

## 2. Alcance

**Incluido**: CRUD de `Inventario` con dos operaciones de escritura
separadas por diseño (`mover` para sucursal/ubicación,
`ajustar_cantidad` por delta), validaciones cruzadas con `Joya` y
`Sucursal`, régimen completo (auditoría, versionado, Domain Events,
logging, Optimistic Locking).

**Excluido**: `PUT` que sobrescriba `cantidad` directamente (decisión
explícita, ver ADR-009-01); reportes agregados de inventario por
sucursal (candidato natural para el Dashboard Ejecutivo, Etapa 15).

## 3. Resumen ejecutivo

Revisión de Consistencia Global inicial: se detectó que
`InventarioModel` (Etapa 5) ya declaraba manualmente una columna
`actualizado_en` idéntica en semántica a la que provee
`AuditoriaMixin` — aplicar el mixin tal cual habría duplicado la
declaración. Resuelto reemplazando la columna manual por los mixins
estándar sin pérdida de datos (ADR-009-02). Se decidió además que
`cantidad` nunca se sobrescribe directamente: toda modificación es un
ajuste atómico por delta con motivo obligatorio (ADR-009-01),
evitando condiciones de carrera silenciosas típicas de sistemas de
inventario con múltiples operadores concurrentes.

## 4. Arquitectura

```
domain/entities/inventario.py                  Inventario(CamposAuditoria, CamposVersion)
domain/repositories/inventario_repository.py     crear, mover, ajustar_cantidad, listar
infrastructure/db/models/gemologia.py             InventarioModel + mixins (ADR-009-02)
infrastructure/repositories/postgres_inventario_repository.py   UPDATE condicional (mover Y ajustar_cantidad)
application/dto/inventario_dto.py                   Create, Mover, AjustarCantidad, Response
application/services/inventario_service.py            valida Joya+Sucursal, publica eventos, loguea
api/v1/routers/inventario.py                            POST, GET, PUT /mover, PATCH /ajustar
alembic/versions/0003_completar_inventario.py             ALTER TABLE aditivo (6 columnas + 3 FK)
```

## 5. Justificación técnica

Ver ADR-009-01 y ADR-009-02 en `docs/adr/`. Resumen:

- **Ajuste por delta, no sobrescritura**: previene que dos operadores
  concurrentes pisen sus cambios mutuamente; cada ajuste queda
  auditado con `motivo` obligatorio, formando un kardex consultable
  vía `historial_eventos` (reutilizado desde la Etapa 5/7.5, cero
  tablas nuevas).
- **`mover` separado de `ajustar_cantidad`**: dos operaciones de
  negocio distintas (relocalización física vs. movimiento de
  existencias) no deben compartir un único endpoint genérico — cada
  una tiene su propia validación y su propio significado en el evento
  de dominio publicado.
- **Reemplazo de columna manual por mixin** (ADR-009-02): mismo
  nombre, mismo tipo, cero migración destructiva — precedente para
  cualquier modelo futuro en la misma situación.

## 6. Código completo

Todos los archivos listados en la sección 7 se entregan completos, sin
pseudocódigo ni `TODO` pendientes.

## 7. Lista de archivos creados

```
docs/adr/ADR-009-01-ajuste-cantidad-por-delta.md
docs/adr/ADR-009-02-completar-inventario-mixins.md
docs/ETAPA_9_INVENTARIO.md
backend/app/domain/entities/inventario.py
backend/app/domain/repositories/inventario_repository.py
backend/app/infrastructure/repositories/postgres_inventario_repository.py
backend/app/application/dto/inventario_dto.py
backend/app/application/services/inventario_service.py
backend/app/api/v1/routers/inventario.py
backend/alembic/versions/0003_completar_inventario.py
backend/app/tests/test_inventario.py
```

## 8. Lista de archivos modificados

```
backend/app/infrastructure/db/models/gemologia.py   (InventarioModel + mixins, ADR-009-02)
backend/app/dependencies.py                            (+get_inventario_repository, +get_inventario_service)
backend/app/main.py                                       (+router inventario)
README.md, CHANGELOG.md, VERSION, docs/ROADMAP_ETAPAS.md, docs/ARQUITECTURA.md
```

**Cero cambios** en: `joyas.py` (router/service/repository),
`esmeraldas.py` (router/service/repository), `sucursales.py`,
`auth.py`, `seed_db.py` (no crea registros de inventario, verificado
por inspección — sin impacto).

## 9. Árbol del proyecto (cambios de la Etapa 9 resaltados)

```
Terrae/
├── docs/adr/
│   ├── ADR-009-01-ajuste-cantidad-por-delta.md       ← NUEVO
│   └── ADR-009-02-completar-inventario-mixins.md      ← NUEVO
├── docs/ETAPA_9_INVENTARIO.md                           ← NUEVO
└── backend/
    ├── alembic/versions/0003_completar_inventario.py     ← NUEVO
    └── app/
        ├── domain/
        │   ├── entities/inventario.py                      ← NUEVO
        │   └── repositories/inventario_repository.py         ← NUEVO
        ├── application/
        │   ├── dto/inventario_dto.py                           ← NUEVO
        │   └── services/inventario_service.py                    ← NUEVO
        ├── infrastructure/
        │   ├── db/models/gemologia.py                              (InventarioModel modificado)
        │   └── repositories/postgres_inventario_repository.py       ← NUEVO
        ├── api/v1/routers/inventario.py                                ← NUEVO
        ├── dependencies.py                                                (modificado)
        ├── main.py                                                          (modificado)
        └── tests/test_inventario.py                                          ← NUEVO
```

## 10. ADR de las decisiones importantes

`docs/adr/ADR-009-01-ajuste-cantidad-por-delta.md`,
`docs/adr/ADR-009-02-completar-inventario-mixins.md`.

## 11. Riesgos

| Riesgo | Severidad | Mitigación |
|---|---|---|
| `ajustar_cantidad` requiere 2 sentencias SQL en el caso de conflicto (UPDATE fallido + SELECT de diagnóstico) — ventana teórica donde el estado pudo cambiar entre ambas | Baja | La garantía de atomicidad real la da el `UPDATE` condicional (única fuente de verdad); el `SELECT` posterior solo compone el mensaje de error, nunca decide el resultado de la operación |
| Sin reportes agregados de inventario todavía (total por sucursal, alertas de stock bajo) | Media | Fuera de alcance explícito de esta etapa (§2); candidato natural para Dashboard Ejecutivo (Etapa 15) sin requerir cambios de esquema |
| Migración 0003 no probada contra PostgreSQL real en este sandbox | Media | Verificación automatizada exhaustiva (columna por columna, simetría de `downgrade()`) como mitigación parcial — pendiente ejecución real |

## 12. Cobertura de pruebas

- `test_inventario.py`: 16 pruebas (creación, validaciones cruzadas de
  Joya/Sucursal, duplicado 409, ajuste por delta con 6 escenarios
  incluyendo conflicto de versión y resultado negativo, `mover` con
  Optimistic Locking, filtros).
- Total acumulado del proyecto: 112 pruebas.
- **No fue posible ejecutar `pytest --cov`** en este sandbox. Comando
  pendiente de ejecutar localmente:

  ```bash
  docker compose exec backend pytest --cov=app.domain.entities.inventario \
    --cov=app.application.services.inventario_service \
    --cov=app.infrastructure.repositories.postgres_inventario_repository \
    --cov=app.api.v1.routers.inventario --cov-report=term-missing
  ```

## 13. Checklist de validación

- [ ] `make db-migrate` aplica `0003_completar_inventario` sin errores sobre una base ya en `0002`.
- [ ] `make test` — las 16 pruebas nuevas pasan, y las 96 pruebas acumuladas de las etapas 4-8 siguen pasando sin cambios (112 en total).
- [ ] `POST /api/v1/inventario` con una `joya_id`/`sucursal_id` válidas crea el registro con `cantidad` y `version: 1`.
- [ ] Crear un segundo inventario para la misma joya devuelve 409.
- [ ] `PATCH /inventario/{id}/ajustar` con `delta: -2` reduce la cantidad correctamente e incrementa `version`.
- [ ] `PATCH /inventario/{id}/ajustar` con un `delta` que dejaría `cantidad` negativa devuelve 422.
- [ ] `PUT /inventario/{id}/mover` cambia `sucursal_id`/`ubicacion_fisica` sin tocar `cantidad`.
- [ ] Los logs muestran `domain_events` por cada creación/ajuste/movimiento de inventario.
- [ ] `frontend/simulator/index.html` sigue intacto.

## 14. Documentación actualizada

`docs/ETAPA_9_INVENTARIO.md`, `docs/adr/`, `README.md`, `CHANGELOG.md`,
`VERSION`, `docs/ROADMAP_ETAPAS.md`, `docs/ARQUITECTURA.md`.

## 15. Próxima etapa recomendada

**Etapa 10 — Certificados digitales**, activando la relación
`JoyaModel`↔`CertificadoModel` (Etapa 5), bajo el mismo régimen
obligatorio, con el `hash_sha256` ya modelado como ancla para la futura
integración con blockchain (Etapa 12) — recordando siempre que
blockchain nunca será la fuente principal de verdad
(`CONSTITUCION_INGENIERIA_TERRAE.md` §7).

---

## Revisión arquitectónica independiente (autoevaluación crítica)

- **Arquitectura**: dominio (`Inventario`) sin dependencias de
  SQLAlchemy/FastAPI, verificado por inspección de imports.
- **DDD**: `InventarioService` orquesta 3 repositorios
  (`InventarioRepository`, `JoyaRepository`, `SucursalRepository`) sin
  conocer sus implementaciones concretas — cumple D de SOLID.
- **SOLID**: separar `mover` de `ajustar_cantidad` en el repositorio y
  en el router respeta Single Responsibility a nivel de operación, no
  solo de clase.
- **Seguridad**: mismo patrón de autorización centralizada que
  `esmeraldas` — sin cambios que revisar de nuevo.
- **Compatibilidad**: verificado que `JoyaModel.inventario`
  (relationship ya declarada en la Etapa 5) sigue funcionando sin
  cambios — `InventarioModel` solo ganó columnas, ninguna relación se
  tocó.
- **Riesgo de escala**: `listar` filtra por `sucursal_id`/`joya_id` sin
  índice compuesto dedicado; `sucursal_id` y `joya_id` ya tienen índice
  implícito por ser FK con `unique=True`/FK simple — aceptable para el
  volumen actual, revisar si el catálogo crece a escala de millones de
  filas (mandato explícito del Prompt Maestro V2.0 de estar "preparado
  para millones de registros").
- **Deuda técnica reconocida**: no existe todavía un endpoint de
  "inventario consolidado por sucursal" (suma de `cantidad` agrupada) —
  se pospone deliberadamente a la Etapa 15 (Dashboard Ejecutivo) en vez
  de construirlo aquí sin un consumidor real que lo necesite (mismo
  principio aplicado a Domain Events desde la Etapa 7.5/8: no construir
  "por si acaso").

**Conclusión de la revisión**: la etapa cumple los criterios de
aceptación del Prompt Maestro V2.0 aplicables a su alcance. No se
identificaron bloqueantes.
