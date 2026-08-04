# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto sigue [Versionado Semántico](https://semver.org/lang/es/).

## [0.10.0] - 2026-08-03

### Añadido — Etapa 10: Certificados digitales y activos multimedia trazables

Incorpora la condición transversal establecida por el usuario: todo
archivo multimedia (fotografía, imagen microscópica, certificado
escaneado, recurso visual) se trata como activo trazable con
metadatos completos.

- `ActivoMultimedia` (dominio): entidad polimórfica
  (`entidad_tipo`/`entidad_id`) que sustituye a `FotografiaModel`
  (Etapa 5, sin consumidores nunca construidos — verificado). De los 6
  metadatos exigidos (autor, fecha, dispositivo, versión, hash,
  relación), 4 reutilizan directamente `CamposAuditoria`/`CamposVersion`
  ya obligatorios desde la Etapa 8; solo `dispositivo` y `hash_sha256`
  son campos nuevos (ADR-010-01).
- `ActivoMultimediaService`: validadores de existencia extensibles por
  `entidad_tipo` (registrados para Joya, Esmeralda, Certificado) sin
  modificar la clase (Open/Closed Principle).
- `Certificado` (dominio) completado: auditoría parcial que conserva
  `emitido_en`/`emitido_por` (Etapa 5) sin duplicarlos con
  `creado_en`/`creado_por` (ADR-010-02), más `version`.
- `CertificadoService`: emisión con `numero_certificado`/`hash_sha256`
  generados server-side (nunca por el cliente), regla de unicidad de
  certificado vigente por joya, revocación con Optimistic Locking.
- Routers `/api/v1/certificados` y `/api/v1/activos-multimedia`.
- Migración `0004_activos_multimedia`: `DROP TABLE fotografias`
  (única operación destructiva del proyecto hasta ahora, justificada
  exhaustivamente — sin consumidores), `CREATE TABLE activos_multimedia`,
  `ALTER TABLE certificados` (aditivo).
- 2 ADRs nuevos (ADR-010-01, ADR-010-02).
- 17 pruebas nuevas (129 en total acumuladas).

### Cambiado

- `JoyaModel`: removida relationship `fotografias` (nunca usada).
- `app/dependencies.py`: `+4` funciones de DI (aditivo).
- `app/main.py`: `+2` routers (aditivo).

### Notas

- Revisión de Consistencia Global confirmó, por búsqueda exhaustiva,
  que `FotografiaModel` nunca tuvo consumidores — condición necesaria
  para justificar el único `DROP TABLE` del proyecto hasta la fecha.
- No fue posible ejecutar `pytest --cov` ni aplicar la migración
  contra PostgreSQL real en este sandbox; ver checklist pendiente en
  `docs/ETAPA_10_CERTIFICADOS_Y_MULTIMEDIA.md`.

## [0.9.0] - 2026-08-02

### Añadido — Etapa 9: Inventario

- `Inventario` (dominio): primera entidad **completamente nueva**
  (no completada desde una versión parcial) construida directamente
  bajo el régimen obligatorio de `CONSTITUCION_INGENIERIA_TERRAE.md` §4.
- `InventarioRepository` + `PostgresInventarioRepository`: `crear`,
  `mover` (sucursal/ubicación, Optimistic Locking estándar),
  `ajustar_cantidad` (delta atómico, ADR-009-01 — nunca sobrescritura
  directa de `cantidad`), `listar`.
- `InventarioService`: valida que `Joya` y `Sucursal` existan, valida
  unicidad 1:1 con la joya, publica Domain Events, registra versión,
  usa logging estructurado.
- Router `/api/v1/inventario`: `POST`, `GET` (+ `GET /joya/{joya_id}`),
  `PUT /{id}/mover`, `PATCH /{id}/ajustar` (delta + motivo obligatorio).
- Migración `0003_completar_inventario`: 100% aditiva, verificada
  exhaustivamente contra el modelo ORM.
- 2 ADRs nuevos (ADR-009-01, ADR-009-02).
- 16 pruebas nuevas (112 en total acumuladas).

### Cambiado

- `InventarioModel` (Etapa 5): columna `actualizado_en` declarada
  manualmente reemplazada por `AuditoriaMixin`/`VersionadoMixin`
  (ADR-009-02) — mismo nombre/tipo de columna, cero migración
  destructiva.
- `app/dependencies.py`: `+get_inventario_repository()`, `+get_inventario_service()` (aditivo).
- `app/main.py`: `+router inventario` (aditivo).

### Notas

- Revisión de Consistencia Global detectó que `InventarioModel` ya
  tenía una columna `actualizado_en` manual idéntica en semántica a la
  del mixin — resuelto sin pérdida de datos (ver ADR-009-02).
- No fue posible ejecutar `pytest --cov` ni aplicar la migración
  contra PostgreSQL real en este sandbox; ver checklist pendiente en
  `docs/ETAPA_9_INVENTARIO.md`.

## [0.8.0] - 2026-08-01

### Añadido — Etapa 8: Gestión de esmeraldas

Bajo un nuevo Prompt Maestro Permanente V2.0 (JJ GROUP SAS) que exige
Revisión de Consistencia Global antes de cada etapa:

- `CONSTITUCION_INGENIERIA_TERRAE.md`: nuevo documento rector,
  consolidando los principios vigentes desde la Etapa 1 más los
  mandatos del Prompt Maestro V2.0.
- `docs/adr/`: primeros 4 Architecture Decision Records del proyecto
  (ADR-008-01 a ADR-008-04).
- `docs/CONVENCIONES_ENTIDADES.md` actualizado: Domain Events y
  Optimistic Locking pasan de opcionales a **obligatorios** para toda
  entidad nueva (ver ADR-008-01).
- `Esmeralda` completada (Etapa 7 la dejó parcial): hereda
  `CamposAuditoria` + `CamposVersion` (nuevo mixin de dominio,
  `domain/shared/versionado.py`).
- `EsmeraldaRepository` extendido con `crear`, `actualizar` (Optimistic
  Locking vía `UPDATE` condicional atómico, ADR-008-04), `listar`,
  `desactivar`, `obtener_por_codigo_interno`.
- `EsmeraldaService`: primera entidad que publica Domain Events
  (`EntidadCreadaEvent`/`EntidadActualizadaEvent`/`EntidadDesactivadaEvent`),
  registra versión (reutilizando `historial_eventos`, Etapa 5) y usa
  logging estructurado.
- `app/infrastructure/events/consumers.py`: primer consumidor real del
  `EventBus` (logging de auditoría genérico, ADR-008-03).
- Router `/api/v1/esmeraldas` completo (administrador o joyero).
- Migración `0002_completar_esmeraldas`: 100% aditiva (6 columnas + 3
  FK), verificada exhaustivamente contra el modelo ORM.
- 19 pruebas nuevas, incluyendo 2 pruebas de regresión explícita
  confirmando que `JoyaService` (Etapa 7) sigue funcionando igual.

### Cambiado

- `app/dependencies.py`: `+get_registrador_version()`, `+get_esmeralda_service()` (aditivo).
- `app/main.py`: `+router esmeraldas`, `+configurar_event_bus()` (aditivo).

### Notas

- Contradicción detectada y resuelta antes de escribir código: la
  convención previa (Etapa 7.5) trataba Domain Events/Optimistic
  Locking como opcionales; el nuevo Prompt Maestro V2.0 los exige sin
  excepción. Resuelto mediante `CONSTITUCION_INGENIERIA_TERRAE.md`
  como documento de mayor jerarquía (ver Revisión de Consistencia
  Global al inicio de la etapa).
- No fue posible ejecutar `pytest --cov` ni aplicar la migración
  contra PostgreSQL real en este sandbox (sin red ni Docker); ver
  checklist de validación pendiente en
  `docs/ETAPA_8_GESTION_ESMERALDAS.md`.

## [0.7.5] - 2026-07-31

### Añadido — Etapa 7.5: Arquitectura Empresarial Transversal

Infraestructura transversal para las etapas 8-22, sin agregar
funcionalidad de negocio ni romper compatibilidad:

- **Auditoría**: `CamposAuditoria` (dominio, `domain/shared/auditoria.py`)
  y `AuditoriaMixin`/`VersionadoMixin` (ORM, `infrastructure/db/mixins.py`)
  — `creado_en`/`actualizado_en`/`creado_por`/`actualizado_por`/`eliminado_en`/`eliminado_por`
  reutilizables por entidades futuras, sin aplicarse retroactivamente a
  `Usuario`/`Sucursal`/`Joya`/`Esmeralda`.
- **Versionado**: `RegistradorVersion` + `HistorialEventoRegistradorVersion`
  (`infrastructure/events/version_registry.py`), reutilizando la tabla
  `historial_eventos` (Etapa 5) en vez de crear una tabla nueva.
- **Domain Events**: `DomainEvent` + `EntidadCreadaEvent` /
  `EntidadActualizadaEvent` / `EntidadDesactivadaEvent`
  (`domain/shared/events.py`), y `EventBus`/`InMemoryEventBus`
  (`infrastructure/events/event_bus.py`) — sin consumidores registrados.
- **Logging estructurado**: `FormateadorJSON` + `get_logger()`
  (`infrastructure/logging/structured_logger.py`) y
  `RequestLoggingMiddleware` (`api/v1/middleware/request_logging.py`),
  que agrega el header `X-Request-ID` a toda respuesta.
- **Concurrencia**: `ConflictoDeVersionError` + `verificar_version()`
  (`application/concurrencia.py`), preparación para optimistic locking.
- `docs/CONVENCIONES_ENTIDADES.md`: convenciones obligatorias desde la
  Etapa 8 para adoptar toda esta infraestructura de forma consistente.
- `docs/ETAPA_7_5_ARQUITECTURA_EMPRESARIAL.md`: documentación completa
  (arquitectura, justificación, decisiones, riesgos, validación).
- 33 pruebas nuevas en 6 archivos.

### Cambiado

- `app/main.py`: registrado `RequestLoggingMiddleware` (agrega header
  `X-Request-ID`, no modifica ningún endpoint existente).
- `app/dependencies.py`: agregada `get_event_bus()` (aditivo).

### Notas

- Cero endpoints modificados, cero contratos rotos, cero módulos
  reescritos — verificado explícitamente con pruebas de integración
  (`test_request_logging_middleware.py`) que confirman que login,
  health y manejo de errores existentes se comportan exactamente igual.
- No fue posible ejecutar `pytest --cov` en este sandbox (sin red ni
  Docker) para confirmar el 90% de cobertura exigido por el Prompt
  Maestro; ver checklist pendiente en
  `docs/ETAPA_7_5_ARQUITECTURA_EMPRESARIAL.md`.

## [0.7.0] - 2026-07-30

### Añadido — Etapa 7: Gestión de joyas

- Entidad de dominio `Joya` con máquina de estados del ciclo de vida
  comercial (`en_taller`, `disponible`, `reservada`, `en_reparacion`,
  `dada_de_baja`; `vendida` reservado al futuro módulo de Ventas,
  Etapa 19) — `Joya.puede_transicionar_a()` encapsula la matriz de
  transiciones válidas en el dominio puro.
- Entidad `Esmeralda` y `EsmeraldaRepository` **parcial** (solo
  `obtener_por_id` y `esta_vinculada_a_joya_activa`), lo mínimo que
  `JoyaService` necesita para validar — el CRUD completo llega en la
  Etapa 8, extendiendo esta misma interfaz.
- `PostgresJoyaRepository`, `PostgresEsmeraldaRepository`
  (infraestructura).
- `JoyaService`: validación de esmeralda/sucursal asociadas (deben
  existir), regla de unicidad esmeralda↔joya activa, cambio de estado
  controlado (nunca permite `vendida` directamente).
- Router `/api/v1/joyas` (administrador **o** joyero pueden escribir,
  a diferencia de `sucursales` que es solo administrador), con
  `PATCH /joyas/{id}/estado` dedicado en vez de `DELETE` (la baja
  lógica ya es un estado de la máquina de estados).
- 14 pruebas nuevas en `test_joyas.py`.
- `docs/ETAPA_7_GESTION_JOYAS.md`: documentación completa (máquina de
  estados, reglas de negocio, decisiones de autorización).

### Notas

- `test_joyas.py` requiere PostgreSQL real corriendo, igual que
  `test_sucursales.py` (Etapa 6).
- No fue posible ejecutar `pytest` contra PostgreSQL real en este
  sandbox (sin red ni Docker); validado con `py_compile` y revisión
  manual de la matriz de transiciones y la cadena de inyección de
  dependencias.

## [0.6.0] - 2026-07-30

### Añadido — Etapa 6: API REST base

- Convención de paginación (`ParametrosPaginacion`, `RespuestaPaginada[T]`)
  reutilizable por cualquier endpoint de listado futuro.
- Excepciones genéricas de aplicación (`app/application/errors.py`) y
  manejadores centralizados (`app/api/v1/error_handlers.py`) — los
  routers de dominio nuevos ya no necesitan `try/except HTTPException`.
- Primer router CRUD completo de referencia: `sucursales`
  (`domain/entities/sucursal.py` → `SucursalRepository` →
  `PostgresSucursalRepository` → `SucursalService` →
  `api/v1/routers/sucursales.py`), con paginación, filtrado (`tipo`,
  `ciudad`, `activa`), control de acceso por rol y baja lógica.
- 12 pruebas nuevas en `test_sucursales.py` (CRUD, paginación, filtrado,
  roles).
- `docs/ETAPA_6_API_REST_BASE.md`: documentación completa de las
  convenciones establecidas.

### Notas

- Decisión de diseño: a partir de esta etapa, las entidades nuevas
  (`sucursales` y las de la Etapa 7 en adelante) tienen únicamente
  implementación PostgreSQL, sin el fallback JSON que sí tiene
  `usuarios` (histórico de la Etapa 4, previa a la base de datos).
- `test_sucursales.py` requiere PostgreSQL real corriendo (a diferencia
  de `test_auth.py`, que puede usar el fallback JSON) — ver
  `docs/ETAPA_6_API_REST_BASE.md`.
- No fue posible ejecutar `pytest` contra PostgreSQL real en este
  sandbox (sin red ni Docker); validado con `py_compile` y revisión
  manual de la cadena de inyección de dependencias.

## [0.5.0] - 2026-07-30

### Añadido — Etapa 5: Base de datos inicial

- Modelo de datos PostgreSQL completo: 24 tablas en 9 módulos por
  dominio (`usuarios`, `organizacion`, `gemologia`, `multimedia`,
  `laboratorio`, `certificacion`, `blockchain`, `comercial`,
  `auditoria`), con relaciones, `ON DELETE` explícito por FK, y
  `naming_convention` para constraints deterministas.
- `backend/alembic/`: configuración completa de Alembic (`env.py`
  conectado a `app.config.get_settings()`) + migración inicial
  `0001_esquema_inicial` (escrita a mano y verificada exhaustivamente:
  columna por columna contra los modelos, orden topológico de FKs, y
  `downgrade()` simétrico a `upgrade()`).
- `PostgresUsuarioRepository`: implementa `UsuarioRepository` sobre
  PostgreSQL. `app/dependencies.py` ahora elige esta implementación o
  `JsonUsuarioRepository` según `DATABASE_URL` — único archivo
  modificado para el cambio de persistencia, tal como se prometió en la
  Etapa 4.
- `backend/app/scripts/seed_db.py`: siembra sucursal + 2 esmeraldas y 2
  joyas de referencia (Muzo/Chivor), idempotente.
- `docker-entrypoint.dev.sh`: aplica migraciones automáticamente al
  iniciar el contenedor backend.
- `Makefile`: nuevos comandos `db-migrate`, `db-downgrade`,
  `db-revision`, `db-seed`.
- `test_postgres_user_repository.py`: 7 pruebas contra SQLite en
  memoria (válido: ningún modelo usa tipos específicos de PostgreSQL).
- `docs/ETAPA_5_BASE_DE_DATOS.md`: documentación completa (catálogo de
  tablas, ERD simplificado, decisiones, validación).

### Corregido

- Columna `acuñado_en` (tabla `nfts`) renombrada a `acunado_en`: se
  detectó un carácter no-ASCII que rompía la consistencia del esquema
  (100% ASCII en el resto de columnas) y complicaría exports/integraciones.

### Notas

- No fue posible ejecutar la migración contra PostgreSQL real ni
  `alembic revision --autogenerate` en este sandbox (sin red ni Docker);
  la migración inicial se escribió a mano y se validó con scripts de
  verificación automatizada en vez de ejecución real. Ver
  `docs/ETAPA_5_BASE_DE_DATOS.md` para el checklist pendiente de validar
  localmente.
- `database/migrations/` y `database/seeds/` (creadas como placeholder
  en la Etapa 1) permanecen vacías a propósito: Alembic y el script de
  siembra terminaron viviendo junto al código de la app
  (`backend/alembic/`, `backend/app/scripts/`) por necesitar los mismos
  modelos y configuración — ver nota en `database/README.md`.

## [0.4.0] - 2026-07-29

### Añadido — Etapa 4: Sistema de autenticación y roles (JWT)

- Dominio: entidad `Usuario`, enum `RolUsuario` (administrador, joyero,
  auditor, cliente), interfaz `UsuarioRepository`.
- Aplicación: `AuthService` (registrar, autenticar, refrescar, obtener
  usuario desde token), DTOs (`RegistroRequest`, `LoginRequest`,
  `TokenResponse`, `UsuarioResponse`), excepciones de dominio.
- Infraestructura: `JsonUsuarioRepository` (persistencia intercambiable
  por PostgreSQL en la Etapa 5), `JWTHandler` (PyJWT, tokens `access` +
  `refresh` con claim `type`), hashing de contraseñas con bcrypt.
- API: router `/api/v1/auth` (`/registro`, `/login`, `/refrescar`,
  `/yo`, `/solo-administradores`), dependencias `get_current_user` y
  `require_roles` reutilizables en futuros endpoints protegidos.
- 4 usuarios de demostración sembrados automáticamente (uno por rol).
- Suite de pruebas `test_auth.py` con 12 casos (registro, login, roles,
  refresh, tokens inválidos).
- Frontend: `AuthContext` (persistencia de sesión en `localStorage`,
  refresh automático), `LoginForm.tsx` (primer componente construido
  como React idiomático desde cero, ya que el simulador no incluye
  pantalla de acceso), ruta `/acceso`.
- `docs/ETAPA_4_AUTENTICACION_ROLES.md`: documentación completa.

### Notas

- Persistencia en JSON por diseño (`app/infrastructure/data/usuarios.json`,
  excluido de Git); la migración a PostgreSQL en la Etapa 5 solo
  requiere reemplazar la implementación en `app/dependencies.py`.
- La protección de la vista de backoffice migrada (`/ecosistema`) con
  roles reales se pospone a la Etapa 16, cuando ese módulo se reescriba
  con estado de React idiomático.
- No fue posible ejecutar `pytest` en el sandbox de esta conversación
  (sin acceso a red para instalar dependencias); ejecutar `make test`
  localmente para validar las 12 pruebas nuevas.

## [0.3.0] - 2026-07-29

### Añadido — Etapa 3: Migración del simulador a componentes reales

- CSS del simulador extraído verbatim a `frontend/src/styles/simulador-terrae.css`
  (952 líneas, cero cambios de diseño).
- HTML de las 4 vistas + shell global + modales extraído verbatim a 6
  módulos TypeScript en `frontend/src/lib/simulator/fragments/`.
- Motor JS del simulador (530 líneas, 32 funciones) extraído verbatim a
  `frontend/src/lib/simulator/engine-source.ts`, inyectado en tiempo de
  ejecución como `<script>` real para preservar el scope global que
  requieren los 114 atributos `onclick="..."` conservados.
- `EcosistemaShell.tsx`: componente raíz que ensambla CSS + fragmentos +
  motor JS.
- Ruta real de Next.js `/ecosistema` (`app/ecosistema/page.tsx` +
  `EcosistemaClient.tsx`, con `dynamic import` y `ssr:false`).
- `docs/ETAPA_3_MIGRACION_SIMULADOR.md`: documentación completa de la
  estrategia, decisiones, conflictos resueltos y validación.

### Corregido

- `frontend/tailwind.config.js`: `corePlugins.preflight` desactivado
  para no pisar el reset CSS propio del simulador.
- `frontend/src/app/layout.tsx`: removidas las clases Tailwind del
  `<body>` global (conflicto de especificidad CSS con la regla
  `body{...}` del simulador).
- `frontend/src/app/page.tsx`: estilos del placeholder movidos a un
  `<main>` interno; ahora enlaza a `/ecosistema` además del simulador
  original.

### Notas

- El simulador original (`frontend/simulator/index.html`) permanece sin
  ninguna modificación, verificado en cada paso de esta etapa.
- La conversión de la interactividad (`onclick`/`getElementById`) a
  estado de React idiomático se difiere intencionalmente a las etapas de
  dominio (7, 8, 10, 12, 13, 15, 16), cuando cada módulo se conecte a la
  API real. Ver justificación completa en
  `docs/ETAPA_3_MIGRACION_SIMULADOR.md`.

## [0.2.0] - 2026-07-28

### Añadido — Etapa 2: Configuración del entorno y herramientas

- `docker-compose.yml` con 4 servicios: `db` (PostgreSQL 16), `adminer`,
  `backend` (FastAPI con hot-reload) y `frontend` (Next.js con hot-reload).
- **Backend**: esqueleto FastAPI en `backend/app/` con `main.py` (endpoints
  `/` y `/health`), `config.py` (settings centralizadas vía
  pydantic-settings), `requirements.txt` / `requirements-dev.txt`,
  `pyproject.toml` (ruff, black, mypy, pytest configurados), suite de
  pruebas de humo (`app/tests/test_health.py`), `Dockerfile.dev`.
- **Frontend**: esqueleto Next.js 14 + TypeScript + Tailwind en
  `frontend/src/app/` (`layout.tsx`, `page.tsx`, `globals.css`),
  `package.json`, `tsconfig.json`, `next.config.js`,
  `tailwind.config.js` (con los tokens oficiales de marca Terrae),
  ESLint + Prettier configurados, `Dockerfile.dev`.
- Página placeholder en `/` que enlaza al simulador de referencia servido
  en `/simulator/index.html`.
- `scripts/sync-simulator.sh`: sincroniza (copia, nunca mueve)
  `frontend/simulator/` hacia `frontend/public/simulator/` para que el
  dev server de Next.js pueda servirlo.
- `scripts/setup.sh`: bootstrap de primer arranque (crea `.env`,
  sincroniza el simulador, valida que Docker esté instalado).
- `Makefile` con comandos unificados: `up`, `down`, `logs`, `lint`,
  `format`, `test`, `sync-simulator`, etc.
- `.editorconfig`, `.nvmrc` (Node 20), `.python-version` (3.11).
- `.pre-commit-config.yaml` (ruff, prettier, checks básicos), excluyendo
  siempre `frontend/simulator/`.
- `.vscode/extensions.json` y `.vscode/settings.json` para consistencia
  del equipo (format-on-save, exclusión del simulador del watcher).
- `.dockerignore` para backend y frontend.

### Cambiado

- `.gitignore` actualizado con exclusiones de Next.js (`.next/`,
  `next-env.d.ts`) y de la copia generada `frontend/public/simulator/`.

### Notas

- El simulador (`frontend/simulator/index.html`) permanece sin ninguna
  modificación; el frontend real en `frontend/src/` es, por ahora, solo
  un placeholder de infraestructura. La migración funcional ocurre en la
  Etapa 3.
- No se implementó lógica de negocio en el backend; solo un endpoint de
  salud para validar el entorno de punta a punta.

## [0.1.0] - 2026-07-28

### Añadido — Etapa 1: Arquitectura y estructura del repositorio

- Estructura profesional del monorepo `Terrae/` con separación por dominio:
  `frontend/`, `backend/`, `database/`, `blockchain/`, `ai/`, `docs/`, `scripts/`.
- Simulador original (`frontend/simulator/index.html`) incorporado como fuente
  de verdad visual/funcional, sin modificaciones.
- Activos de marca (logotipo Terrae en 4 variantes: color horizontal, negro
  vertical, dorado sobre negro vertical, monograma dorado sobre negro)
  incorporados en `frontend/simulator/assets/brand/`.
- Archivos base de repositorio: `README.md`, `.gitignore`, `.env.example`,
  `LICENSE`, `CHANGELOG.md`, `VERSION`.
- Documentación técnica inicial en `docs/`:
  - `ARQUITECTURA.md`
  - `MANUAL_INSTALACION.md`
  - `MANUAL_DESARROLLADOR.md`
  - `IDENTIDAD_VISUAL.md`
  - `ROADMAP_ETAPAS.md`
- Definición del plan de ~22 etapas de desarrollo hasta producción.

### Notas

- Ninguna funcionalidad de backend, base de datos, IA o blockchain fue
  implementada en esta etapa; es exclusivamente estructural y documental.
- El simulador permanece 100% funcional e intacto como referencia visual.

[0.10.0]: https://github.com/<tu-usuario>/Terrae/releases/tag/v0.10.0
[0.9.0]: https://github.com/<tu-usuario>/Terrae/releases/tag/v0.9.0
[0.8.0]: https://github.com/<tu-usuario>/Terrae/releases/tag/v0.8.0
[0.7.5]: https://github.com/<tu-usuario>/Terrae/releases/tag/v0.7.5
[0.7.0]: https://github.com/<tu-usuario>/Terrae/releases/tag/v0.7.0
[0.6.0]: https://github.com/<tu-usuario>/Terrae/releases/tag/v0.6.0
[0.5.0]: https://github.com/<tu-usuario>/Terrae/releases/tag/v0.5.0
[0.4.0]: https://github.com/<tu-usuario>/Terrae/releases/tag/v0.4.0
[0.3.0]: https://github.com/<tu-usuario>/Terrae/releases/tag/v0.3.0
[0.2.0]: https://github.com/<tu-usuario>/Terrae/releases/tag/v0.2.0
[0.1.0]: https://github.com/<tu-usuario>/Terrae/releases/tag/v0.1.0
