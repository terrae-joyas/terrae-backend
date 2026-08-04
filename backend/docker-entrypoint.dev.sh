#!/usr/bin/env bash
# ============================================================
# Entrypoint de desarrollo del backend Terrae.
#
# Aplica las migraciones de Alembic (idempotente: si ya están
# aplicadas, no hace nada) antes de arrancar el servidor. Esto
# garantiza que `make up` deje siempre el esquema de base de datos
# actualizado sin pasos manuales adicionales.
# ============================================================
set -e

echo "🔧 Aplicando migraciones de base de datos (alembic upgrade head)..."
alembic upgrade head

echo "✅ Migraciones al día. Iniciando servidor..."
exec "$@"
