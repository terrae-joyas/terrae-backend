# ADR-008-04 — Optimistic Locking vía `UPDATE` condicional

## Estado
Aceptado — Etapa 8

## Contexto

`app/application/concurrencia.py` (Etapa 7.5) dejó preparado el
contrato (`ConflictoDeVersionError`, `verificar_version()`) pero ninguna
entidad lo implementaba todavía. `Esmeralda` es la primera en
necesitarlo (ADR-008-01).

Dos mecanismos posibles:
1. Leer la entidad, comparar `version` en Python, y solo entonces
   hacer `UPDATE` (con posible condición de carrera entre la lectura y
   la escritura).
2. `UPDATE` condicional atómico:
   `UPDATE esmeraldas SET ..., version = version + 1 WHERE id = :id AND version = :version_esperada`,
   verificando `rowcount == 0` para detectar conflicto.

## Decisión

Se implementa el mecanismo 2 (`UPDATE` condicional atómico) en
`PostgresEsmeraldaRepository.actualizar()`. Es la única opción que
realmente previene la condición de carrera: con el mecanismo 1, dos
requests concurrentes podrían leer la misma versión antes de que
cualquiera escriba, y ambos "pasarían" la verificación en Python.

`session.execute(update(...).where(...))` seguido de
`result.rowcount == 0 → raise ConflictoDeVersionError` es atómico a
nivel de base de datos (una sola sentencia SQL), sin necesidad de
`SELECT ... FOR UPDATE` ni transacciones explícitas adicionales.

## Consecuencias

- El DTO `EsmeraldaUpdateRequest` incluye `version: int` obligatorio —
  cambio de contrato consciente, cubierto por pruebas (esta es una
  entidad *nueva* en cuanto a su CRUD completo, no rompe nada previo).
- `EsmeraldaService.actualizar()` no necesita llamar a
  `verificar_version()` explícitamente: el repositorio ya garantiza la
  atomicidad y traduce el conflicto a `ConflictoDeVersionError`
  directamente. `verificar_version()` queda disponible para casos
  donde la comparación ocurra en la capa de aplicación antes de tocar
  el repositorio (ej. validaciones compuestas).
- Precedente para toda entidad futura con Optimistic Locking: replicar
  este mismo patrón de `UPDATE` condicional, no el de lectura-comparación-escritura.
