# Arquitectura del Ecosistema Digital Terrae

## 1. Visión general

Terrae es un ecosistema compuesto por cuatro dominios técnicos que se
desarrollarán de forma incremental sobre la base visual y funcional ya
validada en el simulador (`frontend/simulator/index.html`):

```
┌─────────────────────────────────────────────────────────────────┐
│                        USUARIOS FINALES                          │
│   Clientes · Joyeros · Auditores · Administradores Terrae         │
└───────────────────────────────┬───────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │        FRONTEND          │
                    │  React + Next.js + TS     │
                    │  (migrado desde simulador) │
                    └────────────┬────────────┘
                                 │ REST (JSON) / JWT
                    ┌────────────▼────────────┐
                    │         BACKEND           │
                    │   FastAPI (Python)         │
                    │   Clean Architecture        │
                    │   Repository Pattern        │
                    └───┬─────────┬──────────┬───┘
                        │         │          │
           ┌────────────▼──┐ ┌────▼─────┐ ┌──▼─────────────┐
           │  PostgreSQL     │ │ SIEGEM Lab│ │  EmeraldChain   │
           │  (SQLAlchemy)    │ │ IA (PyTorch│ │  Blockchain     │
           │  Datos estructu- │ │ OpenCV,    │ │  Polygon/       │
           │  rados del        │ │ YOLO)      │ │  Solidity       │
           │  negocio          │ │            │ │                 │
           └──────────────────┘ └────────────┘ └─────────────────┘
```

## 2. Principios arquitectónicos

- **Clean Architecture / DDD**: separación estricta entre dominio, casos de
  uso, infraestructura y presentación. El dominio no depende de frameworks.
- **Repository Pattern**: toda persistencia se accede vía interfaces de
  repositorio, permitiendo cambiar de almacenamiento (JSON → PostgreSQL) sin
  tocar la lógica de negocio.
- **Service Layer**: la lógica de negocio vive en servicios, no en los
  controladores/endpoints.
- **DTOs y validación**: entrada y salida de la API validadas con Pydantic;
  nunca se exponen directamente los modelos de dominio.
- **Gateway de Blockchain simulable**: un `BlockchainGateway` con
  implementación simulada y real, intercambiable por variable de entorno
  (`BLOCKCHAIN_GATEWAY_MODE`), permite desarrollar y probar sin depender de
  la red Polygon en todo momento.
- **Identidad visual inmutable**: el frontend real replica exactamente el
  diseño del simulador; ningún cambio visual se introduce fuera de un
  proceso de diseño explícito.

## 3. Dominios funcionales (mapeados a los módulos del simulador)

> Desde la Etapa 3, cada fila también existe como ruta real de Next.js
> en `/ecosistema` (componentización verbatim), documentada en
> `docs/ETAPA_3_MIGRACION_SIMULADOR.md`.

| Dominio | Módulo del simulador | Futuro subsistema técnico |
|---|---|---|
| Sitio público / Landing | Vista "Sitio Público" | `frontend/src` (Next.js, páginas públicas) |
| Colecciones | Sección `#colecciones` | API de catálogo de joyas/esmeraldas |
| Pasaporte Digital | Vista "Pasaporte Digital" | API de piezas + certificados + blockchain |
| Certificado oficial | Pasaporte Digital Deluxe | Servicio de generación de certificados (PDF/QR) |
| SIEGEM Lab | Vista "SIEGEM Lab" | Módulo de IA (`ai/`) + API de inferencia |
| Blockchain Experience | Tabs dentro del Pasaporte | Módulo `blockchain/` (EmeraldChain) |
| Centro de Operaciones | Vista "Centro de Operaciones" | Backoffice: auth, roles, inventario, auditoría |

## 4. Stack tecnológico

| Capa | Tecnología |
|---|---|
| Frontend | HTML5, CSS3, JavaScript, TypeScript, React, Next.js |
| Backend | Python, FastAPI |
| Base de datos | PostgreSQL + SQLAlchemy (ORM) |
| Autenticación | JWT |
| IA | PyTorch, OpenCV, YOLO |
| Blockchain | Polygon, Solidity (Smart Contracts), MetaMask (wallet) |
| Storage | Supabase (datos/archivos), IPFS vía Pinata (metadatos NFT) |
| Contenedores | Docker |
| Repositorio | GitHub (GitHub Desktop compatible) |

## 5. Estructura de carpetas y su rol

```
Terrae/
├── frontend/
│   ├── simulator/     → Fuente de verdad visual (HTML original, intacto)
│   ├── public/         → Activos estáticos de la app real (etapa 3+)
│   └── src/             → Código React/Next.js real (etapa 3+)
├── backend/
│   └── app/
│       ├── domain/        → Entidades y reglas de negocio puras (futuro)
│       ├── application/    → Casos de uso / servicios (futuro)
│       ├── infrastructure/  → Repositorios, DB, blockchain gateway (futuro)
│       └── api/               → Routers FastAPI, DTOs (futuro)
├── database/
│   ├── migrations/     → Migraciones (Alembic, etapa 5)
│   └── seeds/           → Datos de referencia (piezas TR-2026-00842, etc.)
├── blockchain/
│   ├── contracts/      → Smart contracts Solidity (EmeraldChain)
│   └── scripts/         → Scripts de despliegue/verificación
├── ai/
│   ├── models/          → Modelos entrenados (EfficientNetB0, U-Net, etc.)
│   └── datasets/         → Datasets de inclusiones y calibración
└── docs/                 → Toda la documentación técnica del proyecto
```

## 6. Decisiones técnicas de la Etapa 1

| Decisión | Justificación |
|---|---|
| Monorepo único (`Terrae/`) | Simplifica la instalación con GitHub Desktop y la trazabilidad de commits entre frontend/backend/blockchain/IA en un proyecto de este tamaño. |
| El simulador se mueve a `frontend/simulator/` sin tocarlo | Cumple la regla obligatoria de no romper el simulador existente y lo mantiene como referencia viva mientras se construye la app real en `frontend/src`. |
| Separación por dominio (`backend`, `database`, `blockchain`, `ai`) en la raíz | Facilita que cada especialista (backend, blockchain, IA) trabaje de forma independiente y que cada etapa futura sea funcional por sí sola. |
| `.env.example` documentado desde la Etapa 1 | Deja explícita, desde el inicio, toda la configuración que necesitará el sistema completo, evitando sorpresas en etapas posteriores. |
| Licencia propietaria | El proyecto es un activo estratégico de EmGroup SAS orientado a adquisición/valuación, no un proyecto open source. |

## 7. Infraestructura de desarrollo (Etapa 2)

El entorno local se orquesta con Docker Compose (`docker-compose.yml`) y se
opera con comandos unificados vía `Makefile`:

```
┌─────────────────────────────────────────────────────────┐
│                    docker-compose.yml                     │
│                                                             │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌─────────┐ │
│  │  frontend  │  │  backend   │  │    db      │  │ adminer  │ │
│  │  Next.js    │  │  FastAPI    │  │ PostgreSQL  │  │  (UI DB)  │ │
│  │  :3000       │  │  :8000       │  │  :5432       │  │  :8080     │ │
│  │  hot-reload   │  │  hot-reload   │  │  16-alpine    │  │            │ │
│  └───────────┘  └───────────┘  └───────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────┘
```

- **backend**: contenedor Python 3.11 con `uvicorn --reload`; monta
  `./backend` como volumen para reflejar cambios de código sin rebuild.
  En esta etapa solo expone `/` y `/health` (validación de entorno).
- **frontend**: contenedor Node 20 con `next dev`; monta `./frontend`
  como volumen (excluyendo `node_modules` y `.next` vía volúmenes
  anónimos). En esta etapa muestra una página placeholder con los tokens
  oficiales de marca y un enlace al simulador.
- **db**: PostgreSQL 16, con `healthcheck` para que el backend espere a
  que la base de datos esté lista antes de arrancar. Sin esquema todavía
  (se define en la Etapa 5).
- **adminer**: cliente web ligero para inspeccionar la base de datos
  durante el desarrollo, sin instalar herramientas adicionales.

### Calidad de código

| Herramienta | Ámbito | Configuración |
|---|---|---|
| `ruff` | Lint + orden de imports (Python) | `backend/pyproject.toml` |
| `black` | Formateo (Python) | `backend/pyproject.toml` |
| `mypy` | Tipado estático (Python) | `backend/pyproject.toml` |
| `pytest` | Pruebas (Python) | `backend/pyproject.toml` |
| `eslint` | Lint (TypeScript/React) | `frontend/.eslintrc.json` |
| `prettier` | Formateo (TypeScript/React) | `frontend/.prettierrc.json` |
| `pre-commit` | Hooks de commit (ambos) | `.pre-commit-config.yaml` |

En todos los casos, `frontend/simulator/` y su copia servible
`frontend/public/simulator/` están explícitamente excluidos de linters,
formateadores y watchers, para no alterar la fuente de verdad visual.

### El simulador dentro de la infraestructura Docker

`frontend/simulator/` sigue siendo la única fuente editable. Para que sea
accesible vía el dev server de Next.js (`http://localhost:3000/simulator/`),
`scripts/sync-simulator.sh` genera una copia en `frontend/public/simulator/`,
carpeta que Next.js sirve de forma estática y que está excluida de Git
(se regenera, nunca se versiona duplicada).

## 8. Capa de datos (Etapa 5)

El modelo de datos completo (24 tablas, 9 módulos por dominio) vive en
`backend/app/infrastructure/db/models/`, documentado en detalle —
catálogo de tablas, ERD y decisiones de normalización — en
`docs/ETAPA_5_BASE_DE_DATOS.md`. En resumen:

- **Base declarativa** (`infrastructure/db/base.py`) con
  `naming_convention` fija, para que Alembic genere nombres de
  constraint deterministas entre entornos.
- **Migraciones** con Alembic (`backend/alembic/`), conectadas a la
  misma fuente de configuración que usa el backend en runtime
  (`app.config.get_settings()`), aplicadas automáticamente al iniciar
  el contenedor de desarrollo (`docker-entrypoint.dev.sh`).
- **Repository Pattern en la práctica**: `PostgresUsuarioRepository`
  implementa la misma interfaz `UsuarioRepository` que
  `JsonUsuarioRepository` (Etapa 4). `app/dependencies.py` decide cuál
  usar según `DATABASE_URL` — es el único archivo que cambió para
  migrar de JSON a PostgreSQL, validando en la práctica el principio de
  arquitectura definido desde la Etapa 1 (§2).

## 9. Convenciones de API REST (Etapa 6)

Documentadas en detalle en `docs/ETAPA_6_API_REST_BASE.md`: paginación
(`ParametrosPaginacion`/`RespuestaPaginada[T]`), filtrado vía query
params traducidos a `WHERE` en el repositorio, manejo de errores
centralizado (`app/application/errors.py` +
`app/api/v1/error_handlers.py`), autorización por defecto (lectura
abierta a cualquier autenticado, escritura restringida a
`administrador`), y baja lógica en vez de `DELETE` físico. El router
`sucursales` es la implementación de referencia que todo router de
dominio nuevo (joyas, esmeraldas, certificados...) debe replicar.

## 10. Primer módulo de dominio: joyas (Etapa 7)

`joyas` es la implementación de referencia de un módulo de dominio
"real" (no solo infraestructura transversal como `sucursales`),
documentada en `docs/ETAPA_7_GESTION_JOYAS.md`: entidades de dominio con
lógica propia (`Joya.puede_transicionar_a()`), validaciones cruzadas
entre repositorios (`JoyaService` depende de `EsmeraldaRepository` y
`SucursalRepository` para validar integridad referencial a nivel de
aplicación, no solo de base de datos), y un contrato de repositorio
extendido incrementalmente entre etapas (`EsmeraldaRepository` nace
parcial en la Etapa 7 y se completa en la Etapa 8, sin romper a quien
ya lo consume).

## 11. Infraestructura empresarial transversal (Etapa 7.5)

Documentada en detalle en `docs/ETAPA_7_5_ARQUITECTURA_EMPRESARIAL.md` y
`docs/CONVENCIONES_ENTIDADES.md`. Resumen: `domain/shared/` (campos de
auditoría y Domain Events reutilizables por cualquier entidad futura),
`infrastructure/db/mixins.py` (columnas de auditoría/versión para
modelos ORM nuevos), `infrastructure/events/` (`EventBus` desacoplado,
sin consumidores todavía; registrador de versiones que reutiliza
`historial_eventos` en vez de crear una tabla nueva),
`infrastructure/logging/` (logger JSON estructurado) y
`RequestLoggingMiddleware` (request_id, usuario, duración en cada
request). Ninguna entidad existente (`Usuario`, `Sucursal`, `Joya`,
`Esmeralda`) adopta esta infraestructura retroactivamente — es la base
que las etapas 8 en adelante usarán desde su primer commit.

## 12. Gobierno de ingeniería y primera entidad bajo régimen completo (Etapa 8)

Desde la Etapa 8 el proyecto se rige también por
`CONSTITUCION_INGENIERIA_TERRAE.md` (documento rector de mayor
jerarquía que cualquier convención puntual) y por Architecture Decision
Records en `docs/adr/`. `Esmeralda` es la primera entidad completada
bajo el régimen obligatorio de auditoría, versionado, Domain Events,
logging y Optimistic Locking (ver
`docs/ETAPA_8_GESTION_ESMERALDAS.md` y ADR-008-01 a ADR-008-04) — el
patrón de referencia que toda entidad nueva desde la Etapa 9 debe
replicar, según `docs/CONVENCIONES_ENTIDADES.md`.

## 13. Inventario: primera entidad completamente nueva bajo el régimen (Etapa 9)

`Inventario` (`docs/ETAPA_9_INVENTARIO.md`, ADR-009-01, ADR-009-02) es
la primera entidad construida directamente bajo el régimen obligatorio
de la Etapa 8, sin haber pasado por una fase "parcial" previa. Aporta
un patrón nuevo al catálogo de convenciones: modificación de un valor
acumulativo (`cantidad`) exclusivamente por ajuste atómico basado en
delta, nunca por sobrescritura directa — precedente para cualquier
entidad futura con semántica de "saldo" (ej. tokens fungibles,
Etapa 20).

## 14. Certificados y trazabilidad multimedia (Etapa 10)

`docs/ETAPA_10_CERTIFICADOS_Y_MULTIMEDIA.md`, ADR-010-01, ADR-010-02.
Introduce `ActivoMultimedia`, entidad polimórfica transversal para
cualquier archivo trazable (foto, imagen microscópica, certificado
escaneado, recurso visual), sustituyendo a `FotografiaModel` (Etapa 5,
sin consumidores). Establece el patrón de reutilizar
`CamposAuditoria`/`CamposVersion` para cumplir requisitos de
trazabilidad sin duplicar campos, y el patrón de auditoría parcial
para entidades con campos de dominio preexistentes equivalentes
(`Certificado.emitido_en`/`emitido_por`).

## 15. Próximos pasos arquitectónicos (Etapa 11 en adelante)

- Etapa 11: QR y trazabilidad — activar `QRModel` (Etapa 5) para verificación pública de certificados.
- Etapa 12-13: integración real de blockchain (EmeraldChain) e IA (SIEGEM Lab).
