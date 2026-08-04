# ADR-008-01 — Domain Events y Optimistic Locking pasan de opcionales a obligatorios

## Estado
Aceptado — Etapa 8

## Contexto

`docs/CONVENCIONES_ENTIDADES.md` (Etapa 7.5) establecía que Domain
Events y Optimistic Locking eran **opcionales**, a adoptar solo cuando
una entidad tuviera una necesidad de negocio concreta (ej. alta
contención de escritura). El nuevo Prompt Maestro Permanente V2.0
(JJ GROUP SAS), que rige todas las etapas desde la Etapa 8, establece
en cambio: *"TODA NUEVA ENTIDAD DEBERÁ IMPLEMENTAR: Auditoría,
Versionado, Domain Events, Logging, Optimistic Locking"* — sin
condicionarlo a una necesidad puntual.

Esto es una contradicción directa con la convención previa.

## Decisión

Se adopta el mandato del Prompt Maestro V2.0 como documento rector de
mayor jerarquía (ver `CONSTITUCION_INGENIERIA_TERRAE.md` §14). Domain
Events y Optimistic Locking son obligatorios para toda entidad nueva
desde la Etapa 8, sin excepción por "falta de necesidad puntual".

Para que "obligatorio" no degenere en "publicar eventos que nadie
consume" (lo que la Etapa 7.5 correctamente identificó como deuda
técnica), se exige además que cada etapa que introduzca una entidad
nueva registre al menos un consumidor real de sus eventos — ver
ADR-008-03.

## Consecuencias

- `docs/CONVENCIONES_ENTIDADES.md` §3 y §5 se reescriben en esta etapa
  (no es una entidad de negocio, es documentación de proceso — no
  aplica la restricción de "no reescribir módulos finalizados").
- Toda entidad completada o creada desde la Etapa 8 (empezando por
  `Esmeralda`) paga el costo adicional de: publicar eventos, tener un
  consumidor, y soportar concurrencia optimista en su endpoint de
  actualización.
- Las entidades previas (`Usuario`, `Sucursal`, `Joya`) no se migran
  retroactivamente — ver ADR-008-02 para el caso específico de
  `Esmeralda`, que sí se completa bajo este nuevo régimen por ser la
  entidad objeto de esta etapa.
