# ADR-010-02 — Adaptar el régimen de auditoría en `Certificado` sin duplicar `emitido_en`/`emitido_por`

## Estado
Aceptado — Etapa 10

## Contexto

`CertificadoModel` (Etapa 5) ya declara `emitido_por` (FK a
`usuarios.id`) y `emitido_en` (timestamp) — semánticamente idénticos a
`creado_por`/`creado_en` de `CamposAuditoria` (Etapa 7.5), pero con
nombre de dominio propio (un certificado se "emite", no simplemente se
"crea" — distinción legal/de negocio real en el dominio de
certificación). Aplicar `CamposAuditoria` completo duplicaría estos
dos campos bajo dos nombres distintos para el mismo instante.

## Decisión

Se aplica el régimen de auditoría de forma **parcial y explícita**, no
por herencia ciega de `CamposAuditoria`: `Certificado` conserva
`emitido_por`/`emitido_en` (dominio propio, ya usados desde la
Etapa 5) y añade solo lo que le falta:
`actualizado_en`/`actualizado_por`/`eliminado_en`/`eliminado_por`
(vía composición manual en el dominio, no vía `AuditoriaMixin`
completo en el ORM) más `version` (`CamposVersion`).

Esto es consistente con el principio DRY del Prompt Maestro V2.0: la
obligación es que la información exista y sea consultable, no que los
nombres de columna sean literalmente `creado_en`/`creado_por` en toda
entidad sin excepción.

## Consecuencias

- `CertificadoModel` NO hereda `AuditoriaMixin` (evitaría la colisión
  de nombres); declara sus propias columnas
  `actualizado_en`/`actualizado_por`/`eliminado_en`/`eliminado_por`
  con la misma semántica y tipos que el mixin, más `VersionadoMixin`
  (`version`) que sí se reutiliza sin conflicto.
- El dominio `Certificado` no hereda `CamposAuditoria` (evitaría el
  mismo conflicto de nombres a nivel Python); declara sus propios
  campos equivalentes.
- Precedente: toda entidad futura con campos de auditoría
  preexistentes bajo nombres de dominio (ej. una futura entidad
  `Venta` con `vendido_en`/`vendido_por`) debe resolverse igual —
  conservar el nombre de dominio, añadir solo lo que falte, nunca
  duplicar.
