# ADR-010-01 — `ActivoMultimedia` como entidad polimórfica transversal

## Estado
Aceptado — Etapa 10

## Contexto

El usuario estableció una condición transversal obligatoria: *"Todo
archivo multimedia (fotografía, imagen microscópica, certificado
escaneado o recurso visual) deberá tratarse como un activo trazable,
con metadatos completos (autor, fecha, dispositivo, versión, hash y
relación con la entidad de negocio correspondiente)"*.

`FotografiaModel` (Etapa 5) modelaba esto de forma estrecha (solo
fotos de joyas, sin autor/dispositivo/hash/versión) y **no tiene
ningún consumidor** (verificado por búsqueda exhaustiva: cero
referencias fuera de su propia definición y del `__init__.py` de
modelos) — nunca se construyó su repositorio, servicio ni router.
`CapturaModel` (laboratorio SIEGEM Lab, Etapa 5) tiene el mismo
problema para imágenes microscópicas, y tampoco tiene consumidores.

## Decisión

Se introduce `ActivoMultimedia`, una entidad polimórfica única
(`entidad_tipo` + `entidad_id`, mismo patrón ya usado en
`HistorialEventoModel`/`AuditoriaModel` desde la Etapa 5) que cubre
los 4 tipos de archivo mencionados por el usuario
(`TipoActivoMultimedia`: `FOTO_JOYA`, `IMAGEN_MICROSCOPICA`,
`CERTIFICADO_ESCANEADO`, `RECURSO_VISUAL`), **sustituyendo**
`FotografiaModel` (se elimina: sin consumidores, no es "romper un
módulo terminado").

Insight de diseño clave: de los 6 metadatos exigidos por el usuario
(autor, fecha, dispositivo, versión, hash, relación), **4 ya están
resueltos por la infraestructura de la Etapa 7.5/8** sin escribir
código nuevo:

| Metadato exigido | Campo que lo resuelve |
|---|---|
| Autor | `creado_por` (`CamposAuditoria`) |
| Fecha | `creado_en` (`CamposAuditoria`) |
| Versión | `version` (`CamposVersion`) |
| Relación con la entidad de negocio | `entidad_tipo` + `entidad_id` (propios de esta entidad) |
| Dispositivo | `dispositivo: str \| None` (nuevo, propio de esta entidad) |
| Hash | `hash_sha256: str` (nuevo, propio de esta entidad) |

Solo 2 campos son genuinamente nuevos (`dispositivo`, `hash_sha256`);
el resto es reutilización directa del régimen ya obligatorio desde la
Etapa 8 (`CONSTITUCION_INGENIERIA_TERRAE.md` §4) — cumple DRY al pie
de la letra.

`CapturaModel` (SIEGEM Lab) **no se toca en esta etapa**: pertenece al
alcance de la Etapa 13 (IA); se deja documentado como pendiente de
evaluar si debe migrar a referenciar `ActivoMultimedia` cuando esa
etapa active su pipeline real.

## Consecuencias

- Tabla `fotografias` (Etapa 5) se elimina en la migración
  `0004_activos_multimedia.py`; tabla `activos_multimedia` la
  reemplaza con alcance más amplio.
- `JoyaModel.fotografias` (relationship nunca usada) se remueve; las
  fotos de una joya se consultan vía
  `GET /api/v1/activos-multimedia?entidad_tipo=Joya&entidad_id=...`.
- Sin pipeline de subida de archivos todavía (Etapa 14, "Gestión de
  imágenes y multimedia"): esta etapa establece el **contrato de
  metadatos y trazabilidad**, no el almacenamiento de bytes. `url`
  apunta a un recurso ya alojado externamente; `hash_sha256` lo
  calcula y envía el cliente (o, si en el futuro existe subida
  server-side, se recalculará ahí — sin romper este contrato).
- Precedente para toda entidad futura que necesite adjuntar
  multimedia (esmeraldas, mantenimientos, auditorías): referenciar
  `ActivoMultimedia` vía `entidad_tipo`/`entidad_id`, nunca crear una
  tabla de fotos propia.
