# ADR-009-02 — Completar `InventarioModel` reemplazando su columna manual por los mixins estándar

## Estado
Aceptado — Etapa 9

## Contexto

`InventarioModel` (Etapa 5) ya declaraba manualmente una columna
`actualizado_en` (`DateTime(timezone=True), nullable=False,
server_default=func.now(), onupdate=func.now()`) — exactamente la
misma semántica que `AuditoriaMixin.actualizado_en` (Etapa 7.5).
Aplicar `AuditoriaMixin` tal cual duplicaría la declaración de esa
columna (`sqlalchemy` no permite dos columnas con el mismo nombre en
una clase).

## Decisión

Se elimina la declaración manual de `actualizado_en` en
`InventarioModel` y se reemplaza por `AuditoriaMixin` +
`VersionadoMixin`, igual que `EsmeraldaModel` (Etapa 8, ADR-008-02).
La migración (`0003_completar_inventario.py`) **no toca** la columna
`actualizado_en` ya existente en la base de datos (mismo nombre, mismo
tipo, mismas restricciones) — solo agrega las columnas nuevas
(`creado_en`, `creado_por`, `actualizado_por`, `eliminado_en`,
`eliminado_por`, `version`).

## Consecuencias

- Cero pérdida de datos: la columna física `actualizado_en` no se
  recrea, solo cambia qué clase Python la declara.
- `InventarioModel` queda con exactamente los mismos 6 campos de
  auditoría/versión que `EsmeraldaModel`, consistente con
  `CONSTITUCION_INGENIERIA_TERRAE.md` §4.
- Precedente: cualquier modelo futuro que ya tenga una columna cuyo
  nombre coincida con uno de los mixins debe resolverse así (remover
  la declaración manual duplicada), nunca manteniendo ambas.
