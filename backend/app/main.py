"""
Punto de entrada de la API Terrae.

Etapa 6: convenciones base de la API REST — paginación
(`api/v1/schemas/pagination.py`), manejo de errores consistente
(`api/v1/error_handlers.py`) y primer router CRUD completo de
referencia (`sucursales`).

Etapa 7: primer módulo de dominio real del catálogo (`joyas`), con
reglas de negocio propias (validación de esmeralda/sucursal asociadas,
máquina de estados del ciclo de vida comercial).

Etapa 7.5: infraestructura transversal empresarial — auditoría
(`domain/shared/auditoria.py`, `infrastructure/db/mixins.py`),
Domain Events (`domain/shared/events.py`,
`infrastructure/events/event_bus.py`), logging estructurado
(`infrastructure/logging/`, middleware de request), y preparación de
concurrencia optimista (`application/concurrencia.py`). Ningún
endpoint ni contrato existente cambió — ver
docs/ETAPA_7_5_ARQUITECTURA_EMPRESARIAL.md.

Etapa 8: gestión de esmeraldas (`esmeraldas`) — primera entidad que
implementa el régimen completo de `CONSTITUCION_INGENIERIA_TERRAE.md`
§4 (auditoría, versionado, Domain Events, logging, Optimistic
Locking). El `EventBus` obtiene aquí su primer consumidor real
(`configurar_event_bus`, ADR-008-03). Ver
docs/ETAPA_8_GESTION_ESMERALDAS.md y docs/adr/.

Etapa 9: inventario (`inventario`) — primera entidad completamente
nueva (no completada desde una versión parcial) bajo el mismo régimen.
Ajuste de `cantidad` exclusivamente por delta atómico (ADR-009-01),
nunca sobrescritura directa. Ver docs/ETAPA_9_INVENTARIO.md.

Etapa 10: certificados digitales (`certificados`) y activos multimedia
polimórficos (`activos-multimedia`) — todo archivo multimedia (foto,
imagen microscópica, certificado escaneado, recurso visual) se trata
como activo trazable con metadatos completos (autor, fecha,
dispositivo, versión, hash, relación), reutilizando el régimen de
auditoría/versión ya obligatorio en vez de duplicar campos
(ADR-010-01). `Certificado` adapta el régimen sin duplicar
`emitido_en`/`emitido_por` (ADR-010-02). Ver
docs/ETAPA_10_CERTIFICADOS_Y_MULTIMEDIA.md.

Arquitectura (Clean Architecture, sin cambios desde la Etapa 4):

    app/
    ├── domain/          → entidades y reglas de negocio puras (+ domain/shared/ desde la Etapa 7.5)
    ├── application/       → casos de uso / servicios, DTOs, errores genéricos
    ├── infrastructure/     → repositorios PostgreSQL/JSON, JWT, password hashing, events, logging
    └── api/v1/               → routers FastAPI, esquemas compartidos, dependencias de acceso, middleware

Los módulos de dominio restantes (QR, blockchain, IA, etc.) se
incorporan en las etapas 11 en adelante siguiendo exactamente el mismo
patrón.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.error_handlers import registrar_manejadores_de_errores
from app.api.v1.middleware.request_logging import RequestLoggingMiddleware
from app.api.v1.routers import activos_multimedia as activos_multimedia_router
from app.api.v1.routers import auth as auth_router
from app.api.v1.routers import certificados as certificados_router
from app.api.v1.routers import esmeraldas as esmeraldas_router
from app.api.v1.routers import inventario as inventario_router
from app.api.v1.routers import joyas as joyas_router
from app.api.v1.routers import sucursales as sucursales_router
from app.config import get_settings
from app.dependencies import get_event_bus
from app.infrastructure.events.consumers import suscribir_logging_auditoria

settings = get_settings()

app = FastAPI(
    title="Terrae API",
    description="API del Ecosistema Digital Terrae — trazabilidad y "
    "certificación de esmeraldas y alta joyería colombiana.",
    version="0.10.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)

registrar_manejadores_de_errores(app)

app.include_router(auth_router.router, prefix=f"/api/{settings.api_version}")
app.include_router(sucursales_router.router, prefix=f"/api/{settings.api_version}")
app.include_router(joyas_router.router, prefix=f"/api/{settings.api_version}")
app.include_router(esmeraldas_router.router, prefix=f"/api/{settings.api_version}")
app.include_router(inventario_router.router, prefix=f"/api/{settings.api_version}")
app.include_router(certificados_router.router, prefix=f"/api/{settings.api_version}")
app.include_router(activos_multimedia_router.router, prefix=f"/api/{settings.api_version}")


def configurar_event_bus() -> None:
    """Registra los consumidores de Domain Events (ADR-008-03). Se
    llama una única vez al importar este módulo — idempotente porque
    `get_event_bus()` está cacheado (`lru_cache`) y `suscribir()` en
    este único punto de arranque no se repite en tiempo de ejecución."""
    suscribir_logging_auditoria(get_event_bus())


configurar_event_bus()


@app.get("/health", tags=["Sistema"])
def health_check() -> dict:
    """Verifica que la API está viva y responde correctamente."""
    return {
        "status": "ok",
        "service": "terrae-backend",
        "environment": settings.environment,
        "api_version": settings.api_version,
    }


@app.get("/", tags=["Sistema"])
def root() -> dict:
    """Endpoint raíz — información básica de la API."""
    return {
        "message": "Terrae API — Lo que la tierra esconde, Terrae lo revela.",
        "docs": "/docs",
        "health": "/health",
    }
