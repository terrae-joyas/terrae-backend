# Etapa 10 — Certificados digitales y activos multimedia trazables

## 1. Objetivo de la etapa

Activar `Certificado` (Etapa 5) como entidad real, e incorporar la
condición transversal obligatoria establecida por el usuario: todo
archivo multimedia (fotografía, imagen microscópica, certificado
escaneado, recurso visual) debe tratarse como activo trazable con
metadatos completos (autor, fecha, dispositivo, versión, hash,
relación con la entidad de negocio).

## 2. Alcance

**Incluido**: CRUD de `Certificado` (emitir, revocar, listar) con
generación server-side de número/hash; `ActivoMultimedia`, entidad
polimórfica nueva que sustituye a `FotografiaModel` (Etapa 5, sin
consumidores) cubriendo los 4 tipos de archivo mencionados por el
usuario.

**Excluido**: pipeline real de subida de archivos/bytes (Supabase/S3)
— objeto explícito de la Etapa 14 ("Gestión de imágenes y
multimedia"); esta etapa establece el contrato de metadatos, no el
almacenamiento físico. Migración de `CapturaModel` (SIEGEM Lab) a
`ActivoMultimedia` — pertenece al alcance de la Etapa 13 (IA),
documentado como pendiente de evaluar en ese momento.

## 3. Resumen ejecutivo

Revisión de Consistencia Global inicial: se confirmó, por búsqueda
exhaustiva, que `FotografiaModel` (Etapa 5) nunca tuvo consumidores
(cero repositorio, servicio o router construidos) — permitiendo
sustituirlo por una entidad más general sin romper nada. Se identificó
además que, de los 6 metadatos exigidos por el usuario, 4 ya los
resuelve la infraestructura obligatoria desde la Etapa 8
(`creado_por`=autor, `creado_en`=fecha, `version`=versión), reduciendo
el trabajo genuinamente nuevo a solo 2 campos (`dispositivo`,
`hash_sha256`) — ver ADR-010-01. `CertificadoModel` ya tenía
`emitido_en`/`emitido_por` con semántica equivalente a
`creado_en`/`creado_por` bajo nombre de dominio propio; se resolvió
sin duplicar columnas (ADR-010-02).

## 4. Arquitectura

```
domain/entities/activo_multimedia.py       ActivoMultimedia(CamposAuditoria, CamposVersion) + validación de hash
domain/entities/certificado.py               Certificado(CamposVersion) — auditoría parcial (ADR-010-02)
domain/repositories/activo_multimedia_repository.py
domain/repositories/certificado_repository.py
infrastructure/db/models/multimedia.py         ActivoMultimediaModel (sustituye FotografiaModel)
infrastructure/db/models/certificacion.py        CertificadoModel completado
infrastructure/repositories/postgres_activo_multimedia_repository.py
infrastructure/repositories/postgres_certificado_repository.py   Optimistic Locking en revocar()
application/dto/activo_multimedia_dto.py           validación de formato SHA-256
application/dto/certificado_dto.py
application/services/activo_multimedia_service.py    validadores de existencia extensibles por entidad_tipo
application/services/certificado_service.py            genera numero_certificado + hash_sha256 server-side
api/v1/routers/activos-multimedia.py
api/v1/routers/certificados.py
alembic/versions/0004_activos_multimedia.py               DROP fotografias, CREATE activos_multimedia, ALTER certificados
```

## 5. Justificación técnica

Ver ADR-010-01 y ADR-010-02 en `docs/adr/`. Resumen:

- **Entidad polimórfica única para multimedia** en vez de una tabla
  por tipo de entidad relacionada (`fotos_joya`, `fotos_esmeralda`...):
  DRY — un solo repositorio, un solo servicio, un solo router para
  cualquier archivo multimedia futuro.
- **Reutilización del régimen de auditoría/versión** en vez de crear
  campos `autor`/`fecha`/`version` propios: cumple el mandato del
  usuario con el mínimo código nuevo posible.
- **`numero_certificado` y `hash_sha256` generados server-side**: un
  documento oficial no puede depender de que el cliente invente su
  propio número o hash — coherente con "nunca confiar en el frontend"
  (`CONSTITUCION_INGENIERIA_TERRAE.md` §9).
- **Validadores de existencia extensibles por `entidad_tipo`** en
  `ActivoMultimediaService`: nuevas entidades (Esmeralda ya
  registrada; futuras como Mantenimiento) se conectan sin modificar la
  clase del servicio — Open/Closed Principle (SOLID).

## 6. Código completo

Todos los archivos listados en la sección 7 se entregan completos, sin
pseudocódigo ni `TODO` pendientes.

## 7. Lista de archivos creados

```
docs/adr/ADR-010-01-activo-multimedia-polimorfico.md
docs/adr/ADR-010-02-auditoria-parcial-certificado.md
docs/ETAPA_10_CERTIFICADOS_Y_MULTIMEDIA.md
backend/app/domain/entities/activo_multimedia.py
backend/app/domain/entities/certificado.py
backend/app/domain/repositories/activo_multimedia_repository.py
backend/app/domain/repositories/certificado_repository.py
backend/app/infrastructure/repositories/postgres_activo_multimedia_repository.py
backend/app/infrastructure/repositories/postgres_certificado_repository.py
backend/app/application/dto/activo_multimedia_dto.py
backend/app/application/dto/certificado_dto.py
backend/app/application/services/activo_multimedia_service.py
backend/app/application/services/certificado_service.py
backend/app/api/v1/routers/activos_multimedia.py
backend/app/api/v1/routers/certificados.py
backend/alembic/versions/0004_activos_multimedia.py
backend/app/tests/test_certificados.py
backend/app/tests/test_activos_multimedia.py
```

## 8. Lista de archivos modificados

```
backend/app/infrastructure/db/models/multimedia.py       (FotografiaModel → ActivoMultimediaModel, ADR-010-01)
backend/app/infrastructure/db/models/certificacion.py      (CertificadoModel completado, ADR-010-02)
backend/app/infrastructure/db/models/gemologia.py            (JoyaModel: removida relationship fotografias no usada)
backend/app/infrastructure/db/models/__init__.py                (import actualizado)
backend/app/dependencies.py                                       (+4 funciones de DI, aditivo)
backend/app/main.py                                                  (+2 routers)
README.md, CHANGELOG.md, VERSION, docs/ROADMAP_ETAPAS.md, docs/ARQUITECTURA.md
```

**Cero cambios** en: `joyas.py`, `esmeraldas.py`, `inventario.py`,
`sucursales.py`, `auth.py` (routers/servicios/repositorios), `seed_db.py`
(no referencia `FotografiaModel`, verificado por inspección).

## 9. Árbol del proyecto (cambios de la Etapa 10 resaltados)

```
Terrae/
├── docs/adr/
│   ├── ADR-010-01-activo-multimedia-polimorfico.md    ← NUEVO
│   └── ADR-010-02-auditoria-parcial-certificado.md      ← NUEVO
├── docs/ETAPA_10_CERTIFICADOS_Y_MULTIMEDIA.md              ← NUEVO
└── backend/
    ├── alembic/versions/0004_activos_multimedia.py           ← NUEVO
    └── app/
        ├── domain/
        │   ├── entities/activo_multimedia.py                     ← NUEVO
        │   ├── entities/certificado.py                              ← NUEVO
        │   ├── repositories/activo_multimedia_repository.py           ← NUEVO
        │   └── repositories/certificado_repository.py                    ← NUEVO
        ├── application/
        │   ├── dto/activo_multimedia_dto.py, certificado_dto.py            ← NUEVO
        │   └── services/activo_multimedia_service.py, certificado_service.py ← NUEVO
        ├── infrastructure/
        │   ├── db/models/multimedia.py                                        (reescrito, ADR-010-01)
        │   ├── db/models/certificacion.py                                       (completado, ADR-010-02)
        │   ├── db/models/gemologia.py                                             (relationship removida)
        │   └── repositories/postgres_activo_multimedia_repository.py, postgres_certificado_repository.py ← NUEVO
        ├── api/v1/routers/activos_multimedia.py, certificados.py                    ← NUEVO
        ├── dependencies.py, main.py                                                    (modificados)
        └── tests/test_certificados.py, test_activos_multimedia.py                        ← NUEVO
```

## 10. ADR de las decisiones importantes

`docs/adr/ADR-010-01-activo-multimedia-polimorfico.md`,
`docs/adr/ADR-010-02-auditoria-parcial-certificado.md`.

## 11. Riesgos

| Riesgo | Severidad | Mitigación |
|---|---|---|
| `DROP TABLE fotografias` es destructivo si alguna fila llegó a existir fuera de este control de versiones (ej. insertada manualmente en un entorno real) | Baja | Verificado que ningún servicio/script del proyecto pudo haber escrito ahí; documentado explícitamente para que el equipo confirme en su entorno real antes de aplicar la migración en producción |
| Sin pipeline de subida real, `hash_sha256` depende de que el cliente lo calcule correctamente — un cliente malicioso podría enviar un hash que no corresponda al archivo real en `url` | Media | Aceptable en esta etapa (el contrato de metadatos es el objetivo, no la integridad end-to-end); la Etapa 14 (subida real) recalculará el hash server-side a partir de los bytes recibidos, cerrando esta brecha |
| `entidad_tipo` es un string libre en el DTO, sin `Enum` — un cliente podría enviar `"joya"` en vez de `"Joya"` y el validador no dispararía | Media | Documentado como limitación conocida; los validadores registrados usan comparación exacta de string. Candidato a mejora: normalizar a un `Enum` cuando el catálogo de entidades relacionables se estabilice |
| Migración 0004 no probada contra PostgreSQL real en este sandbox | Media | Verificación automatizada exhaustiva (columnas + mixins + simetría de `downgrade()`) como mitigación parcial |

## 12. Cobertura de pruebas

- `test_certificados.py`: 10 pruebas (emisión, autorización, unicidad
  de certificado vigente, revocación con Optimistic Locking,
  reemisión tras revocar, generación de número/hash únicos, filtros).
- `test_activos_multimedia.py`: 7 pruebas (creación, autorización,
  validación de formato de hash, validación de entidad relacionada,
  extensibilidad para tipos desconocidos, baja lógica, filtros).
- Total acumulado del proyecto: 129 pruebas.
- **No fue posible ejecutar `pytest --cov`** en este sandbox. Comando
  pendiente:

  ```bash
  docker compose exec backend pytest --cov=app.domain.entities.certificado \
    --cov=app.domain.entities.activo_multimedia \
    --cov=app.application.services.certificado_service \
    --cov=app.application.services.activo_multimedia_service \
    --cov=app.api.v1.routers.certificados --cov=app.api.v1.routers.activos_multimedia \
    --cov-report=term-missing
  ```

## 13. Checklist de validación

- [ ] `make db-migrate` aplica `0004_activos_multimedia` sin errores sobre una base ya en `0003`.
- [ ] `make test` — las 17 pruebas nuevas pasan, y las 112 pruebas acumuladas de las etapas 4-9 siguen pasando sin cambios (129 en total).
- [ ] `POST /api/v1/certificados` genera `numero_certificado` (prefijo `CERT-`) y `hash_sha256` (64 caracteres) sin que el cliente los envíe.
- [ ] Emitir un segundo certificado para una joya con certificado vigente devuelve 409.
- [ ] `POST /api/v1/certificados/{id}/revocar` cambia el estado y permite emitir uno nuevo después.
- [ ] `POST /api/v1/activos-multimedia` con un hash inválido (no 64 hex) devuelve 422.
- [ ] `POST /api/v1/activos-multimedia` con `entidad_tipo: "Joya"` y una joya inexistente devuelve 404.
- [ ] `GET /api/v1/activos-multimedia?entidad_tipo=Joya&entidad_id=...` filtra correctamente.
- [ ] `frontend/simulator/index.html` sigue intacto.

## 14. Documentación actualizada

`docs/ETAPA_10_CERTIFICADOS_Y_MULTIMEDIA.md`, `docs/adr/`,
`README.md`, `CHANGELOG.md`, `VERSION`, `docs/ROADMAP_ETAPAS.md`,
`docs/ARQUITECTURA.md`.

## 15. Próxima etapa recomendada

**Etapa 11 — QR y trazabilidad**, activando `QRModel` (Etapa 5),
generando un código QR por certificado que enlace a una vista pública
de verificación — y evaluando si el "certificado escaneado" (imagen
del PDF o similar) se adjunta como `ActivoMultimedia` en ese mismo
flujo, cerrando el ciclo completo de trazabilidad multimedia
establecido en esta etapa.

---

## Revisión arquitectónica independiente (autoevaluación crítica)

- **Arquitectura**: dominio (`Certificado`, `ActivoMultimedia`) sin
  dependencias de SQLAlchemy/FastAPI, verificado por inspección.
- **DDD**: `ActivoMultimedia.__post_init__` valida invariantes del
  propio dominio (formato de hash) sin depender de Pydantic —
  la validación de negocio vive en el dominio, la validación de
  entrada HTTP vive en el DTO (`ActivoMultimediaCreateRequest`); ambas
  existen porque cubren capas distintas (defensa en profundidad).
- **SOLID**: `registrar_validador()` en `ActivoMultimediaService`
  respeta Open/Closed — extender sin modificar.
- **Seguridad**: `numero_certificado`/`hash_sha256` nunca provienen del
  cliente; `usuario_id` de auditoría siempre del JWT verificado, nunca
  del body — mismo patrón ya auditado en etapas anteriores.
- **Compatibilidad**: `DROP TABLE fotografias` es la única operación
  destructiva de todo el proyecto hasta ahora; justificada
  exhaustivamente (ADR-010-01) por ausencia total de consumidores.
  Ningún endpoint de las etapas 4-9 cambió.
- **Riesgo de escala**: `activos_multimedia` indexa `entidad_tipo` y
  `entidad_id` por separado (no un índice compuesto) — aceptable para
  el volumen actual; revisar índice compuesto
  `(entidad_tipo, entidad_id)` si el volumen de archivos por entidad
  crece significativamente (mandato de "preparado para millones de
  registros").
- **Deuda técnica reconocida**: sin pipeline de subida real (Etapa 14
  explícitamente pendiente); `entidad_tipo` como string libre en vez
  de Enum (ver tabla de riesgos, §11).

**Conclusión de la revisión**: la etapa cumple los criterios de
aceptación del Prompt Maestro V2.0 aplicables a su alcance, e
incorpora correctamente la condición transversal de trazabilidad
multimedia solicitada por el usuario. No se identificaron bloqueantes.
