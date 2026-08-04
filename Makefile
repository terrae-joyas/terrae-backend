# ============================================================
# Terrae — Comandos unificados de desarrollo
# Uso: make <comando>
# ============================================================

.PHONY: help up down build logs restart \
        backend-shell frontend-shell db-shell \
        lint format test sync-simulator clean \
        db-migrate db-downgrade db-revision db-seed

help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Levanta todo el entorno (db, adminer, backend, frontend)
	docker compose up --build

up-d: ## Levanta todo el entorno en segundo plano
	docker compose up --build -d

down: ## Detiene todos los servicios
	docker compose down

down-v: ## Detiene todos los servicios y borra el volumen de la base de datos
	docker compose down -v

build: ## Reconstruye las imágenes sin usar caché
	docker compose build --no-cache

logs: ## Muestra logs de todos los servicios en tiempo real
	docker compose logs -f

restart: ## Reinicia todos los servicios
	docker compose restart

backend-shell: ## Abre una shell dentro del contenedor backend
	docker compose exec backend bash

frontend-shell: ## Abre una shell dentro del contenedor frontend
	docker compose exec frontend sh

db-shell: ## Abre psql dentro del contenedor de base de datos
	docker compose exec db psql -U terrae_user -d terrae_db

lint: ## Ejecuta linters de backend y frontend
	docker compose exec backend ruff check .
	docker compose exec frontend npm run lint

format: ## Formatea backend (black) y frontend (prettier)
	docker compose exec backend black .
	docker compose exec frontend npm run format

test: ## Ejecuta la suite de pruebas del backend
	docker compose exec backend pytest

sync-simulator: ## Sincroniza frontend/simulator hacia frontend/public/simulator
	bash scripts/sync-simulator.sh

db-migrate: ## Aplica las migraciones pendientes de Alembic (también se ejecuta automáticamente al iniciar el backend)
	docker compose exec backend alembic upgrade head

db-downgrade: ## Revierte la última migración de Alembic
	docker compose exec backend alembic downgrade -1

db-revision: ## Crea una nueva migración autogenerada a partir de cambios en los modelos (uso: make db-revision MSG="descripcion")
	docker compose exec backend alembic revision --autogenerate -m "$(MSG)"

db-seed: ## Siembra datos de referencia (usuarios demo, sucursal y esmeraldas/joyas canónicas)
	docker compose exec backend python -m app.scripts.seed_db

clean: ## Elimina contenedores, volúmenes e imágenes del proyecto
	docker compose down -v --rmi local
