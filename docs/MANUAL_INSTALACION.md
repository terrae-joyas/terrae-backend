# Manual de Instalación

## Alcance actual (hasta Etapa 2)

El repositorio ya incluye: estructura completa, simulador visual, y un
entorno de desarrollo funcional con Docker (PostgreSQL, Adminer, backend
FastAPI con endpoint de salud, frontend Next.js placeholder). Todavía no
hay lógica de negocio real (eso comienza en la Etapa 3 en adelante).

## Requisitos previos

- [GitHub Desktop](https://desktop.github.com/) (recomendado) o Git CLI.
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
  (incluye Docker Compose) — requerido a partir de la Etapa 2.
- Un navegador web moderno (Chrome, Edge, Safari, Firefox).
- Cuenta de GitHub con acceso al repositorio `Terrae`.

Opcional (solo si se quiere trabajar fuera de Docker):
- Node.js 20 (ver `.nvmrc`).
- Python 3.11 (ver `.python-version`).

## 1. Clonar el repositorio

**Con GitHub Desktop:**
1. `File → Clone Repository...`
2. Seleccionar `Terrae` (o pegar la URL).
3. Elegir carpeta local y clic en **Clone**.

**Con Git CLI:**
```bash
git clone https://github.com/<tu-usuario>/Terrae.git
cd Terrae
```

## 2. Configurar el entorno (primer arranque)

```bash
bash scripts/setup.sh
```

Este script:
- Crea `.env` a partir de `.env.example` (si no existe).
- Sincroniza `frontend/simulator/` → `frontend/public/simulator/` para
  que Next.js pueda servirlo.
- Verifica que Docker esté instalado.

## 3. Levantar el entorno de desarrollo

```bash
make up
# equivalente sin make:
docker compose up --build
```

La primera vez puede tardar varios minutos (descarga de imágenes e
instalación de dependencias). Las siguientes veces es prácticamente
instantáneo gracias a la caché de Docker.

## 4. Verificar que todo funciona

| Servicio | URL | Resultado esperado |
|---|---|---|
| Frontend | http://localhost:3000 | Página "TERRAE" con enlace al simulador |
| Simulador | http://localhost:3000/simulator/index.html | Simulador completo, idéntico al original |
| Backend | http://localhost:8000/health | `{"status": "ok", "service": "terrae-backend", ...}` |
| API Docs | http://localhost:8000/docs | Swagger UI de FastAPI |
| Adminer | http://localhost:8080 | Formulario de login a PostgreSQL (sistema: PostgreSQL, servidor: `db`) |

## 5. Comandos útiles del día a día

```bash
make logs               # ver logs en tiempo real
make down                # detener todo
make lint                 # ejecutar linters (ruff + eslint)
make format                # formatear código (black + prettier)
make test                   # ejecutar pruebas del backend (pytest)
make backend-shell           # shell dentro del contenedor backend
make frontend-shell           # shell dentro del contenedor frontend
make db-shell                  # psql dentro del contenedor de base de datos
```

## 6. Ver el simulador sin Docker (alternativa rápida)

El simulador sigue siendo un archivo HTML autocontenido, sin dependencias:

```bash
cd frontend/simulator
open index.html          # macOS
start index.html         # Windows
xdg-open index.html      # Linux
```

## 7. Variables de entorno

`.env` se genera automáticamente en el paso 2 a partir de `.env.example`.
Para desarrollo local los valores por defecto son suficientes; no se
requieren credenciales reales hasta que se integren blockchain/storage
en etapas posteriores. `.env` nunca se sube al repositorio (`.gitignore`).

## Checklist de validación

- [ ] `bash scripts/setup.sh` corre sin errores.
- [ ] `make up` levanta los 4 servicios (`db`, `adminer`, `backend`, `frontend`) sin errores.
- [ ] http://localhost:8000/health responde `status: ok`.
- [ ] http://localhost:3000 muestra la página placeholder con los tokens de marca correctos.
- [ ] http://localhost:3000/simulator/index.html se ve idéntico al simulador original.
- [ ] http://localhost:8080 (Adminer) conecta correctamente a la base `terrae_db`.
- [ ] `make test` pasa la suite de pruebas de humo del backend.
- [ ] `make lint` no reporta errores críticos.
- [ ] `frontend/simulator/index.html` (el original) permanece sin ninguna modificación.

## Próxima etapa

La **Etapa 3 (Migración del simulador a componentes reales)** comenzará a
convertir cada vista del simulador (`vista-publico`, `vista-pasaporte`,
`vista-siegem`, `vista-backoffice`) en componentes React reales dentro de
`frontend/src/`, manteniendo el diseño exacto documentado en
`docs/IDENTIDAD_VISUAL.md`.
