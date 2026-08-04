# Etapa 6 — API REST base

## Objetivo

Establecer las convenciones transversales de la API REST (paginación,
filtrado, manejo de errores consistente) y construir el primer router
CRUD completo (`sucursales`) como patrón de referencia obligatorio para
los routers de dominio de las etapas 7 en adelante (joyas, esmeraldas,
certificados, etc.).

## Convenciones establecidas

### 1. Paginación

Todo endpoint de listado usa `ParametrosPaginacion` (dependencia de
FastAPI) y devuelve `RespuestaPaginada[T]`:

```
GET /api/v1/sucursales?pagina=1&tamano_pagina=20
```

```json
{
  "items": [ ... ],
  "total": 42,
  "pagina": 1,
  "tamano_pagina": 20,
  "total_paginas": 3
}
```

- `pagina` es 1-indexada (más natural para un consumidor de API que un
  offset 0-indexado interno).
- `tamano_pagina` tiene tope de 100 para evitar listados sin límite que
  degraden el rendimiento.
- El offset/limit interno hacia el repositorio se calcula en
  `ParametrosPaginacion.offset` / `.limit` — los servicios de
  aplicación nunca hacen esa aritmética.

### 2. Filtrado

Filtros como parámetros de query opcionales, traducidos 1:1 a cláusulas
`WHERE` en el repositorio (nunca en el servicio de aplicación, para que
el filtrado use índices de base de datos en vez de traer todo a Python):

```
GET /api/v1/sucursales?tipo=taller&ciudad=Bogotá&activa=true
```

### 3. Manejo de errores consistente

Desde esta etapa, los servicios de aplicación levantan excepciones
genéricas de `app/application/errors.py` en vez de que cada router haga
su propio `try/except HTTPException`:

| Excepción | HTTP |
|---|---|
| `EntidadNoEncontradaError` | 404 |
| `EntidadDuplicadaError` | 409 |
| `OperacionNoPermitidaError` | 422 |
| `ValidacionNegocioError` | 422 |

`app/api/v1/error_handlers.py` las traduce centralizadamente en
`registrar_manejadores_de_errores(app)`, llamado una vez en
`app/main.py`. El contrato de respuesta de error se mantiene igual que
desde la Etapa 4: `{"detail": "<mensaje>"}`.

> El módulo `auth` (Etapa 4) conserva sus propias excepciones locales
> (`CorreoYaRegistradoError`, etc.) por no tocar código ya probado — es
> la única excepción documentada a esta convención.

### 4. Autorización por defecto

Patrón para todo router de dominio nuevo:
- **Lectura** (`GET`): cualquier usuario autenticado (`Depends(get_current_user)`).
- **Escritura** (`POST`/`PUT`/`DELETE`): rol `administrador` por defecto
  (`Depends(require_roles(RolUsuario.ADMINISTRADOR))`), ajustable por
  entidad cuando el dominio lo requiera (ej. un `joyero` podrá crear
  joyas de su propia sucursal desde la Etapa 7).

### 5. Baja lógica, no DELETE físico

`DELETE /api/v1/sucursales/{id}` no borra la fila: pone `activa=False`.
Cualquier entidad con posibles relaciones históricas (joyas, ventas,
inventario) sigue este mismo patrón en las etapas futuras, para no
romper integridad referencial ni perder trazabilidad.

## Router de referencia: sucursales

| Método | Ruta | Rol requerido |
|---|---|---|
| GET | `/api/v1/sucursales` | cualquier autenticado |
| GET | `/api/v1/sucursales/{id}` | cualquier autenticado |
| POST | `/api/v1/sucursales` | administrador |
| PUT | `/api/v1/sucursales/{id}` | administrador |
| DELETE | `/api/v1/sucursales/{id}` | administrador (baja lógica) |

Arquitectura idéntica a `auth` (Etapa 4): `domain/entities/sucursal.py`
→ `domain/repositories/sucursal_repository.py` (interfaz) →
`infrastructure/repositories/postgres_sucursal_repository.py` →
`application/services/sucursal_service.py` → `api/v1/routers/sucursales.py`.

## Decisión: sin fallback JSON para entidades nuevas

A partir de esta etapa, las entidades nuevas (`sucursales` y las que
vengan en la Etapa 7+) tienen **únicamente** implementación PostgreSQL,
a diferencia de `usuarios` (Etapa 4/5, que sí tiene `JsonUsuarioRepository`
como fallback). Motivo: ese fallback existió porque `usuarios` se
construyó *antes* de que la base de datos existiera (Etapa 4, previa a
la Etapa 5); para todo lo construido después de la Etapa 5, PostgreSQL
ya es infraestructura estable, así que mantener un doble camino
JSON/PostgreSQL por cada entidad nueva sería complejidad sin beneficio
real. La interfaz de repositorio se sigue definiendo igual (Clean
Architecture, testeable con SQLite en memoria).

## Validación realizada en este sandbox (sin PostgreSQL ni red reales)

- `python3 -m py_compile` sobre todos los `.py` nuevos y modificados:
  sin errores de sintaxis.
- Revisión manual de que el orden topológico de dependencias de DI
  (`app/dependencies.py`) es correcto y no genera importación circular.
- `diff` confirma que `frontend/simulator/index.html` permanece intacto
  (esta etapa no tocó el frontend).

### Pendiente de validar en un entorno con Docker/PostgreSQL real

- `make test` — a diferencia de `test_auth.py` (que puede correr sin
  PostgreSQL gracias al fallback JSON) y `test_postgres_user_repository.py`
  (que usa SQLite en memoria), **`test_sucursales.py` sí requiere
  PostgreSQL real** corriendo (`PostgresSucursalRepository` no tiene
  fallback ni fue diseñado contra SQLite en esta suite), tal como queda
  configurado automáticamente en `docker compose exec backend pytest`.
- Verificar en Swagger UI (http://localhost:8000/docs) que el esquema
  `RespuestaPaginada_SucursalResponse_` se genera correctamente y que el
  botón "Authorize" (Bearer) protege los endpoints de escritura.

## Checklist de validación (a ejecutar por el desarrollador)

- [ ] `make up` — el backend arranca sin errores con el nuevo router montado.
- [ ] `make test` — las 12 pruebas de `test_auth.py` + 7 de `test_postgres_user_repository.py` + 12 de `test_sucursales.py` pasan.
- [ ] `POST /api/v1/sucursales` con el usuario `admin@terrae.co` crea una sucursal.
- [ ] `POST /api/v1/sucursales` con el usuario `cliente@terrae.co` devuelve 403.
- [ ] `GET /api/v1/sucursales?pagina=1&tamano_pagina=2` pagina correctamente.
- [ ] `GET /api/v1/sucursales?ciudad=Bogotá` filtra correctamente.
- [ ] `DELETE /api/v1/sucursales/{id}` marca `activa=false` sin borrar la fila.
- [ ] `GET /api/v1/sucursales/no-existe` devuelve 404 con `{"detail": "..."}`.
- [ ] `frontend/simulator/index.html` sigue intacto.

## Commits recomendados

```
feat(api): convención de paginación (ParametrosPaginacion, RespuestaPaginada)
feat(api): excepciones genéricas de aplicación y manejadores centralizados
feat(backend): entidad Sucursal, SucursalRepository (dominio)
feat(backend): PostgresSucursalRepository (infraestructura)
feat(backend): SucursalService + DTOs (aplicación)
feat(api): router CRUD de sucursales — patrón de referencia
test(backend): suite de pruebas de sucursales (12 casos: CRUD, paginación, filtrado, roles)
docs: documentar Etapa 6 (convenciones de API REST)
```

## Próxima etapa

**Etapa 7 — Gestión de joyas.** Primer módulo de dominio "real" del
catálogo, siguiendo exactamente el patrón de `sucursales`: CRUD
completo, relación con `esmeraldas` e `inventario` (ya modeladas en la
Etapa 5), y las primeras reglas de negocio específicas del dominio
joyero (ej. no permitir cambiar el `estado` de una joya con una venta
activa).
