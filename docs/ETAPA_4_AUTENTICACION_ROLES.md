# Etapa 4 — Sistema de autenticación y roles (JWT)

## Objetivo

Primer módulo de negocio real del backend, con autenticación completa
(registro, login, refresh token) y control de acceso por rol, siguiendo
Clean Architecture de punta a punta, más una pantalla de login real en
React como caso piloto de conversión idiomática.

## Roles definidos

| Rol | Descripción |
|---|---|
| `administrador` | Control total del backoffice (usuarios, auditoría, configuración) |
| `joyero` | Gestiona piezas, inventario y certificados de su(s) taller(es) |
| `auditor` | Acceso de solo lectura a trazabilidad, blockchain y logs |
| `cliente` | Acceso a su(s) pasaporte(s) digital(es) y garantías (rol por defecto al registrarse) |

## Arquitectura implementada

```
backend/app/
├── domain/
│   ├── entities/user.py              → Usuario, RolUsuario (lógica pura, sin dependencias externas)
│   └── repositories/user_repository.py → interfaz UsuarioRepository (Repository Pattern)
├── application/
│   ├── dto/auth_dto.py                 → RegistroRequest, LoginRequest, TokenResponse, UsuarioResponse
│   └── services/
│       ├── auth_service.py               → AuthService (casos de uso: registrar, autenticar, refrescar)
│       └── exceptions.py                   → excepciones de aplicación
├── infrastructure/
│   ├── security/
│   │   ├── password_hasher.py               → hashing bcrypt (passlib)
│   │   └── jwt_handler.py                     → creación/verificación de JWT (PyJWT)
│   └── repositories/
│       └── json_user_repository.py              → implementación JSON de UsuarioRepository
├── api/v1/
│   ├── dependencies.py                            → get_current_user, require_roles (FastAPI Depends)
│   └── routers/auth.py                              → endpoints /api/v1/auth/*
└── dependencies.py                                    → wiring de DI (único archivo a tocar en la Etapa 5)
```

Cada capa depende solo de la que tiene debajo; el dominio no importa
nada de FastAPI, Pydantic ni JSON.

## Endpoints

| Método | Ruta | Descripción | Protegido |
|---|---|---|---|
| POST | `/api/v1/auth/registro` | Crea un usuario nuevo (rol `cliente`) | No |
| POST | `/api/v1/auth/login` | Autentica y devuelve `access_token` + `refresh_token` | No |
| POST | `/api/v1/auth/refrescar` | Emite un nuevo par de tokens a partir de un `refresh_token` válido | No (requiere refresh_token válido) |
| GET | `/api/v1/auth/yo` | Devuelve los datos del usuario autenticado | Sí (Bearer access_token) |
| GET | `/api/v1/auth/solo-administradores` | Endpoint de demostración de `require_roles` | Sí, rol `administrador` |

## Usuarios de demostración (sembrados automáticamente)

Al arrancar el backend por primera vez (repositorio JSON vacío), se
crean 4 usuarios de referencia, uno por rol. **Contraseña de todos:
`Terrae#2026`** (solo para desarrollo local, nunca usar en producción):

| Correo | Rol |
|---|---|
| admin@terrae.co | administrador |
| joyero@terrae.co | joyero |
| auditor@terrae.co | auditor |
| cliente@terrae.co | cliente |

## Decisiones técnicas

| Decisión | Justificación |
|---|---|
| Persistencia JSON en esta etapa | La base de datos real llega en la Etapa 5. Implementar ya la interfaz `UsuarioRepository` permite migrar a PostgreSQL cambiando solo `app/dependencies.py`, sin tocar `AuthService` ni los routers. |
| Tokens `access` + `refresh` separados, con claim `type` | Evita que un refresh token robado se use directamente como access token, y viceversa; ambos casos se validan explícitamente en `JWTHandler.decodificar_token`. |
| `bcrypt==4.0.1` fijado junto a `passlib==1.7.4` | Combinación conocida por evitar el bug `module 'bcrypt' has no attribute '__about__'` que aparece con versiones más nuevas de bcrypt. |
| Endpoints en español (`/registro`, `/login`, `/refrescar`, `/yo`) | Consistencia con el resto del dominio del proyecto (nombres de entidades, DTOs, mensajes de error), ya establecida desde la Etapa 1. |
| `HTTPBearer` en vez de `OAuth2PasswordBearer` con formulario | La API es consumida por una SPA (Next.js) con JSON, no por un cliente OAuth2 tradicional; simplifica el contrato sin perder el botón "Authorize" de Swagger UI. |
| Login/registro NO extraídos del simulador | El simulador original no incluye pantalla de acceso (asume backoffice ya autenticado). `LoginForm.tsx` se construyó desde cero como React idiomático (`useState`), sirviendo de patrón de referencia para las conversiones progresivas de las etapas de dominio. |

## Frontend — primer caso piloto de React idiomático

- `frontend/src/lib/api/client.ts` — cliente `fetch` tipado, con manejo de errores (`ApiError`).
- `frontend/src/lib/auth/auth-api.ts` — llamadas tipadas a `/api/v1/auth/*`.
- `frontend/src/lib/auth/AuthContext.tsx` — contexto React (`useState`/`useEffect`/`useContext`) que persiste los tokens en `localStorage`, restaura la sesión al recargar, y refresca el `access_token` automáticamente si expiró.
- `frontend/src/components/auth/LoginForm.tsx` — formulario real con `useState` y validación, usando los tokens de marca (`docs/IDENTIDAD_VISUAL.md`).
- Ruta `/acceso` (`app/acceso/page.tsx`) — pantalla de login completa.
- `AuthProvider` envuelve toda la app desde `app/layout.tsx`; la home (`/`) ya muestra el estado real de sesión.

## Pendiente (documentado, no implementado en esta etapa)

- **Proteger `/ecosistema` (backoffice) con el rol autenticado.** Requiere
  decidir cómo el `AuthContext` (React) se comunica con el motor JS
  legado del simulador migrado (Etapa 3), que controla la vista
  `vista-backoffice` por clases CSS, no por rutas de Next.js. Se
  abordará en la Etapa 16 (Centro de operaciones), cuando ese módulo se
  reescriba con estado de React idiomático siguiendo el patrón de
  `LoginForm.tsx`.
- **Endpoints de gestión de usuarios** (listar, editar rol, desactivar)
  — llegan naturalmente junto con el backoffice de usuarios en etapas
  posteriores; el dominio y el repositorio ya están listos para
  soportarlos (`listar_todos`, `actualizar` ya existen en la interfaz).

## Validación realizada en este entorno (sandbox sin red/Docker)

- `python3 -m py_compile` sobre todos los `.py` del backend: sin errores
  de sintaxis.
- Revisión manual de flujo de tokens, claims JWT, y orden de validación
  de campos en `RegistroRequest` (Pydantic v2).
- Balance de llaves/paréntesis verificado en todos los `.ts`/`.tsx`
  nuevos del frontend.
- `diff` confirma que `frontend/simulator/index.html` permanece intacto.
- **No fue posible** ejecutar `pytest` realmente (sin acceso a red para
  instalar `fastapi`, `pydantic`, `passlib`, etc. en este sandbox). El
  archivo `backend/app/tests/test_auth.py` contiene 12 pruebas que
  cubren: registro exitoso, correo duplicado (409), contraseñas no
  coincidentes (422), login exitoso, credenciales inválidas (401),
  acceso sin token (401/403), `/yo` con token válido, refresh de token,
  rechazo de access_token usado como refresh_token, rechazo de rol
  incorrecto en endpoint protegido, y validación de los 4 usuarios
  semilla.

## Checklist de validación (a ejecutar por el desarrollador)

- [ ] `make up` levanta el backend sin errores (revisar `make logs`).
- [ ] `make test` — las 12 pruebas de `test_auth.py` (+ 2 de `test_health.py`) pasan.
- [ ] `POST http://localhost:8000/api/v1/auth/login` con `admin@terrae.co` / `Terrae#2026` devuelve tokens.
- [ ] `GET http://localhost:8000/api/v1/auth/yo` con el `access_token` devuelve los datos del administrador.
- [ ] `GET http://localhost:8000/api/v1/auth/solo-administradores` devuelve 403 con el usuario `cliente@terrae.co`.
- [ ] http://localhost:3000/acceso permite iniciar sesión con cualquiera de los 4 usuarios demo.
- [ ] Tras iniciar sesión, http://localhost:3000/ muestra "Sesión activa" con el nombre y rol correctos.
- [ ] Recargar la página mantiene la sesión (persistencia en `localStorage` + `/yo`).
- [ ] `frontend/simulator/index.html` sigue intacto.

## Commits recomendados

```
feat(backend): entidad Usuario y RolUsuario (dominio)
feat(backend): UsuarioRepository (interfaz) + JsonUsuarioRepository (infraestructura)
feat(backend): JWTHandler y password hashing (infraestructura)
feat(backend): AuthService — registro, login, refresh (aplicación)
feat(backend): router /api/v1/auth con dependencias de rol
feat(backend): sembrar usuarios demo (uno por rol) al arrancar
test(backend): suite de pruebas de autenticación (12 casos)
feat(frontend): cliente API + AuthContext + persistencia de sesión
feat(frontend): LoginForm real y ruta /acceso
docs: documentar Etapa 4 (autenticación y roles)
```

## Próxima etapa

**Etapa 5 — Base de datos inicial.** Modelo de datos PostgreSQL completo
(usuarios, joyas, esmeraldas, certificados, blockchain, NFT, ventas,
inventario, auditoría, etc.), migraciones con Alembic, y la primera
implementación real del patrón "cambiar solo `app/dependencies.py`":
`PostgresUsuarioRepository` reemplazará a `JsonUsuarioRepository` sin
tocar `AuthService` ni los routers de autenticación ya construidos en
esta etapa.
