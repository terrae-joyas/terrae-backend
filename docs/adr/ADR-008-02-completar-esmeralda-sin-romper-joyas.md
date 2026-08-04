# ADR-008-02 — Completar `Esmeralda` bajo el nuevo régimen sin romper `Joyas`

## Estado
Aceptado — Etapa 8

## Contexto

`Esmeralda` (dominio) y `EsmeraldaRepository` (interfaz) se crearon en
la Etapa 7 explícitamente **parciales** (solo `obtener_por_id` y
`esta_vinculada_a_joya_activa`), documentando que la Etapa 8 los
completaría. `JoyaService` (Etapa 7) ya depende de la forma actual de
`Esmeralda` (constructor, atributos) a través de
`PostgresEsmeraldaRepository`.

Completar `Esmeralda` bajo el nuevo régimen obligatorio (ADR-008-01)
significa: agregar `CamposAuditoria`, `CamposVersion`, publicar Domain
Events, y soportar Optimistic Locking — cambios que tocan el
constructor de la entidad y el repositorio ya consumido por Joyas.

## Decisión

Se trata como **completar un módulo explícitamente documentado como
parcial**, no como "reescribir un módulo finalizado" (prohibido por
`CONSTITUCION_INGENIERIA_TERRAE.md` §3). Se procede así:

1. `Esmeralda` pasa a heredar `CamposAuditoria` + `CamposVersion`
   (nuevo mixin, ver `app/domain/shared/versionado.py`), manteniendo
   sus campos propios (`codigo_interno`, `mina_origen`, `quilates`,
   etc.) sin cambios de nombre ni de tipo.
2. `EsmeraldaRepository` se **extiende** (no se reescribe): se agregan
   `crear`, `actualizar`, `listar`; `obtener_por_id` y
   `esta_vinculada_a_joya_activa` (ya usados por `JoyaService`)
   conservan exactamente la misma firma y comportamiento.
3. Se agrega una prueba de regresión explícita
   (`test_joyas.py::test_crear_joya_con_esmeralda_valida` y afines,
   ya existentes desde la Etapa 7) que se vuelve a ejecutar sin
   modificar su código, para confirmar que `JoyaService` sigue
   funcionando exactamente igual tras completar `Esmeralda`.
4. La migración de base de datos (`0002_completar_esmeraldas.py`)
   solo **agrega** columnas nullable/con default a la tabla
   `esmeraldas` ya existente — nunca elimina ni renombra una columna
   usada por `JoyaModel.esmeralda_id` (FK intacta).

## Consecuencias

- `PostgresEsmeraldaRepository._a_entidad()` cambia su implementación
  interna (ahora mapea también los campos de auditoría/versión), pero
  su contrato público (`obtener_por_id(id) -> Esmeralda | None`) es
  idéntico al de la Etapa 7.
- Cero cambios en `JoyaService`, `JoyaRepository`,
  `PostgresJoyaRepository` ni en el router `/api/v1/joyas`.
- Riesgo residual: si `JoyaService` alguna vez accediera a
  `esmeralda.creado_en` asumiendo que es un campo no-opcional (Etapa 7
  lo definía como `datetime` requerido), ahora es `datetime | None`
  (heredado de `CamposAuditoria`). Se verificó por revisión de código
  que `JoyaService` **nunca** lee `creado_en` de una `Esmeralda` — solo
  usa `id` para las validaciones. Riesgo descartado.
