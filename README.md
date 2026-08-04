# TERRAE — Ecosistema Digital

> **Lo que la tierra esconde, Terrae lo revela.**

Plataforma tecnológica para trazabilidad, certificación científica y pasaporte digital de esmeraldas y alta joyería colombiana, respaldada por inteligencia artificial (SIEGEM Lab) y blockchain (EmeraldChain).

Este repositorio es la **base técnica real** del Ecosistema Digital Terrae, construida progresivamente a partir del simulador visual/funcional ya existente (`frontend/simulator/index.html`), que define la identidad de marca, la navegación y la experiencia de usuario de referencia.

---

## 📌 Estado del proyecto

| Etapa | Nombre | Estado |
|---|---|---|
| 1 | Arquitectura y estructura del repositorio | ✅ Completada |
| 2 | Configuración del entorno y herramientas | ✅ Completada |
| 3 | Migración del simulador a componentes reales | ✅ Completada |
| 4 | Autenticación y roles | ✅ Completada |
| 5 | Base de datos inicial | ✅ Completada |
| 6 | API REST base | ✅ Completada |
| 7 | Gestión de joyas | ✅ Completada |
| 7.5 | Arquitectura Empresarial Transversal | ✅ Completada |
| 8 | Gestión de esmeraldas | ✅ Completada |
| 9 | Inventario | ✅ Completada |
| 10 | Certificados digitales (+ activos multimedia trazables) | ✅ Completada |
| 11 | QR y trazabilidad | ⏳ Pendiente |
| ... | Ver `docs/ROADMAP_ETAPAS.md` | |

Versión actual: **v0.10.0** (ver `CHANGELOG.md` y `VERSION`).

> Desde la Etapa 8, el proyecto se rige también por
> `CONSTITUCION_INGENIERIA_TERRAE.md` (documento rector) y por los ADR
> en `docs/adr/`.

---

## 🧱 Estructura del repositorio

```
Terrae/
├── frontend/                  # Cliente web
│   ├── simulator/              # Simulador HTML original — NO SE MODIFICA, fuente visual de verdad
│   ├── public/simulator/        # Copia servible del simulador (generada por scripts/sync-simulator.sh)
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx              # Home placeholder
│   │   │   └── ecosistema/            # Ruta real: ecosistema migrado (Etapa 3)
│   │   ├── components/simulator/       # EcosistemaShell.tsx (componente raíz de la migración)
│   │   ├── lib/simulator/               # Motor JS + fragmentos HTML extraídos verbatim
│   │   └── styles/                       # CSS verbatim del simulador
│   ├── package.json, tsconfig.json, next.config.js, tailwind.config.js
│   └── Dockerfile.dev
├── backend/                   # API REST en FastAPI (Python) + PostgreSQL (Etapa 5)
│   ├── alembic/                 # Migraciones (Alembic) — ver docs/ETAPA_5_BASE_DE_DATOS.md
│   │   └── versions/0001_esquema_inicial.py
│   ├── app/
│   │   ├── main.py                # Endpoints / y /health
│   │   ├── config.py               # Settings centralizadas (pydantic-settings)
│   │   ├── dependencies.py          # DI: elige repositorio JSON o PostgreSQL
│   │   ├── domain/                    # Entidades y reglas de negocio puras
│   │   ├── application/                # Casos de uso (AuthService), DTOs
│   │   ├── infrastructure/
│   │   │   ├── db/                        # Base declarativa, sesión, 24 modelos ORM
│   │   │   ├── repositories/                # JsonUsuarioRepository, PostgresUsuarioRepository
│   │   │   └── security/                      # JWT, hashing de contraseñas
│   │   ├── api/v1/                              # Routers y dependencias de la API
│   │   ├── scripts/seed_db.py                     # Siembra de datos de referencia
│   │   └── tests/                                   # Pruebas (pytest)
│   ├── requirements.txt, requirements-dev.txt, pyproject.toml, alembic.ini
│   ├── docker-entrypoint.dev.sh    # Aplica migraciones automáticamente al iniciar
│   └── Dockerfile.dev
├── database/                  # Documentación del modelo de datos (ver docs/ETAPA_5_BASE_DE_DATOS.md)
│   ├── migrations/              # (placeholder, sin uso — ver database/README.md)
│   └── seeds/                     # (placeholder, sin uso — ver database/README.md)
├── blockchain/                 # Smart contracts EmeraldChain (Solidity / Polygon)
│   ├── contracts/
│   └── scripts/
├── ai/                         # Módulo SIEGEM Lab — IA gemológica (PyTorch/OpenCV/YOLO)
│   ├── models/
│   └── datasets/
├── docs/                       # Documentación técnica, manuales y arquitectura
├── scripts/                    # setup.sh, sync-simulator.sh
├── .github/workflows/            # CI/CD (a definir en etapas posteriores)
├── .vscode/                       # Configuración recomendada del editor
├── docker-compose.yml              # Orquestación: db, adminer, backend, frontend
├── Makefile                         # Comandos unificados (make up, make lint, etc.)
├── .editorconfig, .nvmrc, .python-version
├── .pre-commit-config.yaml
├── .gitignore
├── .env.example
├── LICENSE
├── CHANGELOG.md
└── VERSION
```

## 🎨 Identidad visual (fuente de verdad)

La identidad visual completa está definida y congelada en `frontend/simulator/index.html` y documentada en `docs/IDENTIDAD_VISUAL.md`. **Ninguna etapa futura debe alterar esta identidad**; solo debe convertirse en componentes reales.

## 🚀 Instalación rápida

Ver instrucciones completas en `docs/MANUAL_INSTALACION.md`. Resumen:

```bash
# 1. Clonar el repositorio (o abrir con GitHub Desktop)
git clone https://github.com/<tu-usuario>/Terrae.git
cd Terrae

# 2. Configurar el entorno (crea .env, sincroniza el simulador, valida Docker)
bash scripts/setup.sh

# 3. Levantar todo el entorno de desarrollo
make up
# equivalente sin make: docker compose up --build
```

Servicios disponibles una vez levantado:

| Servicio | URL |
|---|---|
| Frontend (Next.js) | http://localhost:3000 |
| Login (Etapa 4) | http://localhost:3000/acceso |
| Ecosistema migrado (Etapa 3, componentes reales) | http://localhost:3000/ecosistema |
| Simulador de referencia original | http://localhost:3000/simulator/index.html |
| Backend (FastAPI) | http://localhost:8000/health |
| Documentación interactiva de la API | http://localhost:8000/docs |
| Adminer (base de datos) | http://localhost:8080 |

Ver también el simulador de forma directa, sin Docker: `open frontend/simulator/index.html`.

Los módulos de base de datos, IA y blockchain se activarán funcionalmente en las etapas 5, 12 y 13 respectivamente; la infraestructura ya está preparada desde esta etapa.

## 🛠️ Comandos de desarrollo

```bash
make help              # Lista todos los comandos disponibles
make up                 # Levanta todo el entorno (db, adminer, backend, frontend)
make down                # Detiene todos los servicios
make logs                 # Logs en tiempo real de todos los servicios
make lint                  # Linters de backend (ruff) y frontend (eslint)
make format                 # Formateo de backend (black) y frontend (prettier)
make test                    # Suite de pruebas del backend (pytest)
make sync-simulator            # Sincroniza frontend/simulator → frontend/public/simulator
make db-migrate                 # Aplica migraciones pendientes de Alembic
make db-downgrade                # Revierte la última migración
make db-seed                      # Siembra usuarios demo + sucursal + esmeraldas/joyas de referencia
```

## 🗺️ Roadmap completo

Ver `docs/ROADMAP_ETAPAS.md` para el plan detallado de las ~20-25 etapas de desarrollo.

## 👥 Equipo técnico de referencia

Este proyecto se desarrolla siguiendo el **Prompt Maestro Terrae**, que define un enfoque multidisciplinario (CTO, arquitectura de software, backend, frontend, IA, blockchain, DevOps, seguridad, QA) trabajando etapa por etapa, con entrega documentada y validación en cada fase.

## 📄 Licencia

Ver `LICENSE`. Software propietario — Terrae / EmGroup SAS. Todos los derechos reservados.
