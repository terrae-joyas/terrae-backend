# Etapa 5 — Base de datos inicial

## Objetivo

Diseñar el modelo de datos PostgreSQL completo del ecosistema Terrae
(normalizado, con relaciones reales), implementarlo con SQLAlchemy +
Alembic, y migrar el repositorio de usuarios de JSON (Etapa 4) a
PostgreSQL **cambiando solo `app/dependencies.py`**, cumpliendo la
promesa de diseño hecha desde la Etapa 4.

## Catálogo de tablas (24)

| Dominio | Tablas |
|---|---|
| Usuarios y permisos | `usuarios`, `permisos`, `rol_permisos` |
| Organización | `sucursales` |
| Gemología | `esmeraldas`, `joyas`, `inventario` |
| Multimedia | `fotografias` |
| Laboratorio SIEGEM Lab | `microscopios`, `calibraciones`, `capturas` |
| Certificación | `certificados` |
| Blockchain | `registros_blockchain`, `nfts`, `tokens_blockchain`, `qr_codigos` |
| Comercial | `clientes`, `historial_propietarios`, `ventas`, `garantias`, `mantenimientos` |
| Trazabilidad transversal | `auditorias`, `historial_eventos`, `logs_sistema` |

## Diagrama de relaciones (ERD simplificado)

```
usuarios ──┬─< certificados (emitido_por)
           ├─< clientes (usuario_id, 1:1 opcional)
           └─< auditorias (usuario_id)

sucursales ──┬─< joyas
             ├─< inventario
             ├─< microscopios
             ├─< ventas
             └─< mantenimientos

esmeraldas ──┬─< joyas
             └─< capturas

joyas ──┬─< inventario (1:1)
        ├─< fotografias
        ├─< certificados
        ├─< historial_propietarios
        ├─< ventas
        └─< mantenimientos

microscopios ──┬─< calibraciones
               └─< capturas

certificados ──┬─< registros_blockchain (1:1)
               └─< qr_codigos (1:1)

registros_blockchain ──< nfts (1:1)

clientes ──┬─< historial_propietarios
           └─< ventas

ventas ──< garantias (1:1)

permisos ──< rol_permisos (rol como string, no FK — ver decisiones)
```

## Decisiones técnicas

| Decisión | Justificación |
|---|---|
| IDs como `String(36)` (UUID en texto) en vez de tipo `UUID` nativo de Postgres | Portabilidad total: el mismo modelo corre sin cambios contra PostgreSQL (producción) y SQLite (pruebas unitarias rápidas sin Docker), como se demuestra en `test_postgres_user_repository.py`. |
| `rol` como `String(20)` en `usuarios` y `rol_permisos`, no FK a una tabla `roles` | El rol ya es un enum cerrado y estable (`RolUsuario`, Etapa 4) validado en la capa de dominio; una tabla `roles` separada añadiría un JOIN sin beneficio real mientras el conjunto de roles no cambie dinámicamente. `permisos`/`rol_permisos` sí quedan listas para permisos granulares futuros sin rediseñar el esquema. |
| `historial_propietarios` separado de `clientes` | Un propietario histórico de una joya (cadena de custodia) puede no ser un cliente activo de Terrae (herencia, reventa externa registrada manualmente). Modelarlos igual habría forzado crear registros de "cliente" ficticios solo para llevar historial. |
| `auditorias` vs. `historial_eventos` vs. `logs_sistema` como tablas separadas | Tres audiencias y ciclos de vida distintos: seguridad/cumplimiento (quién hizo qué acción sensible), línea de tiempo de negocio de una pieza (cambios de propietario, certificación), y diagnóstico técnico (errores, inferencias de IA). Mezclarlas dificultaría auditorías de seguridad reales. |
| `tokens_blockchain` separado de `nfts` | Un NFT es no-fungible (1 token = 1 certificado); `tokens_blockchain` modela tokens fungibles asociados a una wallet, para un eventual programa de fidelización o fraccionamiento de valor (Etapa 20), sin mezclar semánticas distintas en una sola tabla. |
| `ON DELETE` explícito en cada FK (`CASCADE`, `SET NULL`, `RESTRICT`) | Decisión caso por caso: eliminar una joya elimina en cascada su inventario/fotos/certificados (`CASCADE`), pero no se puede eliminar una esmeralda o sucursal referenciada por una joya existente sin antes desvincularla (`SET NULL`) o bloquear la eliminación de una joya con ventas asociadas (`RESTRICT`). |
| Migración inicial escrita a mano, no autogenerada | Este entorno no tiene acceso a una instancia de PostgreSQL real ni a red para instalar dependencias, por lo que `alembic revision --autogenerate` no se pudo ejecutar. La migración se escribió a mano y se verificó exhaustivamente (ver sección de validación) columna por columna contra los modelos, en vez de confiar en generación automática no verificable en este entorno. |
| Convención de nombres de constraints (`naming_convention` en `Base.metadata`) | Sin ella, Alembic genera nombres de constraint no deterministas entre entornos, lo que rompe `alembic downgrade` de forma sutil meses después. Se fijó desde el primer archivo (`app/infrastructure/db/base.py`). |
| Migraciones automáticas en cada arranque del contenedor backend (`docker-entrypoint.dev.sh`) | `alembic upgrade head` es idempotente (no-op si ya está al día), así que automatizarlo en el entrypoint de desarrollo mantiene `make up` como comando único sin pasos manuales, sin riesgo de aplicar la misma migración dos veces. |

## Migración de usuarios: JSON → PostgreSQL

Tal como se prometió en la Etapa 4, el cambio de persistencia se
resolvió en un único archivo:

```python
# app/dependencies.py
@lru_cache
def get_usuario_repository() -> UsuarioRepository:
    settings = get_settings()
    if settings.database_url:
        repo = PostgresUsuarioRepository(get_session_factory())   # ← Etapa 5
    else:
        repo = JsonUsuarioRepository(settings.usuarios_data_path)  # ← fallback Etapa 4
    _sembrar_usuarios_demo(repo)
    return repo
```

`AuthService`, los DTOs, el router `/api/v1/auth/*` y las dependencias de
la API (`get_current_user`, `require_roles`) no cambiaron ni una línea.
`JsonUsuarioRepository` se conserva en el código (con sus pruebas
originales de la Etapa 4 intactas) como referencia y como opción de
arranque sin Docker/PostgreSQL.

## Corrección detectada durante esta etapa

Se detectó y corrigió un carácter no-ASCII (`ñ`) en el nombre de una
columna (`acuñado_en` → `acunado_en`, tabla `nfts`). Los nombres de
columna con caracteres no-ASCII son válidos en PostgreSQL pero requieren
comillas dobles siempre, complican exports/CSV/integraciones con
herramientas de terceros, y son inconsistentes con el resto del
esquema (100% en ASCII). Se corrigió en el modelo y en la migración, y
se re-verificó la correspondencia completa tras el cambio.

## Validación realizada en este sandbox (sin PostgreSQL ni red reales)

- **Verificación automatizada columna por columna**: script Python que
  compara cada modelo SQLAlchemy contra `op.create_table(...)` de la
  migración — las 24 tablas coinciden exactamente (mismo conjunto de
  columnas reales, excluyendo `relationship()` que no son columnas de
  base de datos).
- **Verificación de orden topológico**: script que confirma que ninguna
  tabla se crea antes que las tablas a las que hace referencia por FK
  (las 24 tablas están en orden válido).
- **Verificación de `downgrade()`**: confirmado que elimina las 24
  tablas en el orden exactamente inverso al de `upgrade()`.
- **Pruebas del repositorio** (`test_postgres_user_repository.py`, 7
  casos): ejecutadas contra SQLite en memoria en vez de PostgreSQL real,
  válido porque ningún modelo usa tipos específicos de PostgreSQL
  (JSONB, ARRAY, UUID nativo) — todos los tipos (`String`, `Boolean`,
  `DateTime`, `Float`, `Integer`) son estándar de SQLAlchemy.
- `python3 -m py_compile` sobre todos los `.py` nuevos: sin errores de
  sintaxis.
- `diff` confirma que `frontend/simulator/index.html` permanece intacto
  (esta etapa no tocó el frontend).

### Pendiente de validar en un entorno con Docker/PostgreSQL real (fuera de este sandbox)

- `make up` con la migración aplicándose automáticamente vía
  `docker-entrypoint.dev.sh` contra PostgreSQL 16 real (no SQLite).
- `make test` — que las pruebas de `test_auth.py` (Etapa 4) sigan
  pasando ahora corriendo contra `PostgresUsuarioRepository` en vez de
  `JsonUsuarioRepository` (la fixture de `test_auth.py` no fija
  `DATABASE_URL`, así que seguirá usando JSON salvo que se actualice
  explícitamente — ver nota de checklist).
- `make db-seed` — confirmar que crea la sucursal y las 2 piezas
  canónicas (`TR-2026-00842` Muzo, `TR-2026-00843` Chivor) sin duplicar
  si se ejecuta más de una vez.
- `make db-downgrade` seguido de `make db-migrate` contra PostgreSQL
  real, para confirmar reversibilidad completa (en este sandbox solo se
  verificó la simetría del código, no la ejecución real contra un motor
  con restricciones de FK activas).

## Checklist de validación (a ejecutar por el desarrollador)

- [ ] `make up` — el backend aplica la migración automáticamente al arrancar (ver `make logs`, debe mostrar "Migraciones al día").
- [ ] `make db-seed` crea la sucursal + 2 esmeraldas + 2 joyas de referencia.
- [ ] Conectarse con Adminer (http://localhost:8080) y confirmar que las 24 tablas existen con sus relaciones.
- [ ] `make test` — las pruebas de `test_auth.py` y `test_postgres_user_repository.py` pasan.
- [ ] `make db-downgrade` revierte limpiamente; `make db-migrate` vuelve a aplicar sin errores.
- [ ] Login con los 4 usuarios demo sigue funcionando igual que en la Etapa 4, ahora respaldado por PostgreSQL.
- [ ] `frontend/simulator/index.html` sigue intacto (esta etapa no tocó el frontend).

## Commits recomendados

```
feat(db): declarative base con naming_convention para constraints
feat(db): modelos ORM completos — 24 tablas en 9 módulos por dominio
feat(db): migración inicial de Alembic (0001_esquema_inicial)
feat(db): PostgresUsuarioRepository — implementa UsuarioRepository
feat(backend): dependencies.py elige repositorio JSON/Postgres según DATABASE_URL
feat(backend): script de siembra de datos de referencia (seed_db.py)
feat(docker): entrypoint que aplica migraciones automáticamente al iniciar
test(db): pruebas de PostgresUsuarioRepository contra SQLite en memoria
fix(db): renombrar columna acuñado_en a acunado_en (caracteres no-ASCII)
docs: documentar Etapa 5 (base de datos, ERD, decisiones)
```

## Próxima etapa

**Etapa 6 — API REST base.** Estructura versionada y documentada de la
API más allá de `/auth`: convenciones de paginación, filtrado, manejo de
errores HTTP consistente, y el primer router CRUD completo (probablemente
`sucursales`, por ser la entidad más simple sin dependencias) como
patrón de referencia para los routers de dominio de las etapas 7 en
adelante (joyas, esmeraldas, certificados...).
