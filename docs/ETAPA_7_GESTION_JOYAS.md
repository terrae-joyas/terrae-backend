# Etapa 7 — Gestión de joyas

## Objetivo

Primer módulo de dominio real del catálogo, sobre el patrón de
referencia establecido en la Etapa 6 (`sucursales`), con reglas de
negocio propias del dominio joyero.

## Reglas de negocio implementadas

1. **Referencia única** — validada en el servicio antes de insertar
   (además de la restricción `UNIQUE` de la base de datos como última
   línea de defensa).
2. **Esmeralda asociada debe existir** — si se indica `esmeralda_id`, se
   valida contra el repositorio antes de crear/actualizar.
3. **Una esmeralda no puede estar en dos joyas activas a la vez** —
   `EsmeraldaRepository.esta_vinculada_a_joya_activa()` verifica que
   ninguna otra joya (con estado distinto de `dada_de_baja`) ya la use.
4. **Sucursal asociada debe existir** — mismo patrón que esmeralda.
5. **Máquina de estados del ciclo de vida comercial** — ver diagrama
   abajo. Los cambios de estado no son un `PUT` genérico: tienen su
   propio endpoint (`PATCH /joyas/{id}/estado`) con transiciones
   explícitamente permitidas.

## Máquina de estados

```
en_taller ──┬──> disponible ──┬──> reservada ──> disponible
            │                  │                    │
            │                  ├──> en_reparacion <──┘
            │                  │         │
            │                  │         └──> en_taller | disponible
            │                  │
            └──> dada_de_baja <┴── (terminal, sin salida)

vendida: SOLO alcanzable por el módulo de Ventas (Etapa 19),
         nunca a través de PATCH /joyas/{id}/estado.
```

`Joya.puede_transicionar_a()` (dominio puro, sin dependencias externas)
encapsula esta matriz — el servicio y el router nunca contienen lógica
de transición hardcodeada, solo la invocan.

### Por qué `vendida` está bloqueada aquí

Si el endpoint de cambio de estado permitiera `vendida` libremente, se
podrían crear joyas marcadas como vendidas sin una venta real (registro
en la tabla `ventas`, Etapa 5) detrás — rompiendo la integridad del
futuro reporte de ventas y del historial de propietarios. El intento
devuelve `422` con un mensaje explícito señalando el módulo correcto.

## Diferencia de autorización respecto a `sucursales`

| Router | Lectura | Escritura |
|---|---|---|
| `sucursales` (Etapa 6) | cualquier autenticado | solo `administrador` |
| `joyas` (Etapa 7) | cualquier autenticado | `administrador` **o** `joyero` |

Decisión: la organización física de la empresa (sucursales) es
exclusiva de administración; el catálogo de piezas es el trabajo diario
del rol `joyero`.

## Sin endpoint DELETE

A diferencia de `sucursales` (que usa `DELETE` para baja lógica vía un
simple booleano `activa`), `joyas` no tiene `DELETE`: la baja lógica ya
es un estado explícito de la máquina de estados (`dada_de_baja`),
alcanzable vía `PATCH /joyas/{id}/estado`. Añadir un `DELETE` paralelo
duplicaría el mismo concepto por dos caminos distintos.

## Alcance deliberadamente parcial: `EsmeraldaRepository`

Esta etapa introduce `domain/repositories/esmeralda_repository.py` con
**solo** `obtener_por_id()` y `esta_vinculada_a_joya_activa()` — lo
mínimo que `JoyaService` necesita para validar. El CRUD completo de
esmeraldas (crear, editar, listar con filtros de mina/quilates/color)
es el objetivo explícito de la **Etapa 8**, que *extenderá* esta misma
interfaz (no la reescribirá) con `crear`, `actualizar` y `listar`. En
las pruebas de esta etapa, las esmeraldas de prueba se insertan
directamente vía el modelo ORM (`_crear_esmeralda_directo()` en
`test_joyas.py`) porque todavía no existe un endpoint para crearlas.

## Endpoints

| Método | Ruta | Rol requerido |
|---|---|---|
| GET | `/api/v1/joyas` | cualquier autenticado |
| GET | `/api/v1/joyas/{id}` | cualquier autenticado |
| POST | `/api/v1/joyas` | administrador o joyero |
| PUT | `/api/v1/joyas/{id}` | administrador o joyero |
| PATCH | `/api/v1/joyas/{id}/estado` | administrador o joyero |

Filtros de listado: `tipo`, `estado`, `sucursal_id`, `esmeralda_id`
(mismo patrón de paginación/filtrado que `sucursales`, Etapa 6).

## Validación realizada en este sandbox (sin PostgreSQL ni red reales)

- `python3 -m py_compile` sobre todos los `.py` nuevos y modificados:
  sin errores de sintaxis.
- Revisión manual de la matriz de transiciones de estado (sin ciclos
  no intencionales, `vendida` y `dada_de_baja` correctamente terminales
  desde este módulo).
- Revisión manual de la cadena de inyección de dependencias
  (`JoyaService` recibe `JoyaRepository` + `EsmeraldaRepository` +
  `SucursalRepository`, sin importaciones circulares).
- `diff` confirma que `frontend/simulator/index.html` permanece intacto
  (esta etapa no tocó el frontend).

### Pendiente de validar en un entorno con Docker/PostgreSQL real

- `make test` — `test_joyas.py` (14 casos) requiere PostgreSQL real,
  igual que `test_sucursales.py` (ver nota de la Etapa 6).
- Confirmar en Swagger UI que `PATCH /joyas/{id}/estado` aparece
  correctamente documentado con el enum `EstadoJoya`.

## Checklist de validación (a ejecutar por el desarrollador)

- [ ] `make up` — el backend arranca sin errores con el router de joyas montado.
- [ ] `make test` — las pruebas de `test_joyas.py` (14 casos) pasan.
- [ ] `POST /api/v1/joyas` como `joyero@terrae.co` crea una joya en estado `en_taller`.
- [ ] `POST /api/v1/joyas` como `cliente@terrae.co` devuelve 403.
- [ ] Crear una joya con `esmeralda_id` de una esmeralda ya usada por otra joya activa devuelve 409.
- [ ] `PATCH /joyas/{id}/estado` con `"vendida"` devuelve 422 con mensaje explicando el módulo de Ventas.
- [ ] `PATCH /joyas/{id}/estado` con una transición inválida (ej. `en_taller` → `en_reparacion`) devuelve 422.
- [ ] `frontend/simulator/index.html` sigue intacto.

## Commits recomendados

```
feat(backend): entidad Esmeralda + EsmeraldaRepository parcial (solo lectura/validación)
feat(backend): entidad Joya con máquina de estados del ciclo de vida comercial
feat(backend): PostgresJoyaRepository, PostgresEsmeraldaRepository (infraestructura)
feat(backend): JoyaService — validaciones de esmeralda/sucursal, cambio de estado controlado
feat(api): router CRUD de joyas (administrador + joyero) con endpoint dedicado de cambio de estado
test(backend): suite de pruebas de joyas (14 casos: CRUD, validaciones, máquina de estados)
docs: documentar Etapa 7 (gestión de joyas)
```

## Próxima etapa

**Etapa 8 — Gestión de esmeraldas.** Completa `EsmeraldaRepository` con
`crear`, `actualizar` y `listar` (filtros por mina de origen, rango de
quilates, tratamientos), y su propio router CRUD siguiendo el mismo
patrón. `JoyaService` no necesitará ningún cambio: ya consume la
interfaz completa desde esta etapa.
