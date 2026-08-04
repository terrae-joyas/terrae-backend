"""completar esmeraldas: auditoria y version — Etapa 8

Revision ID: 0002_completar_esmeraldas
Revises: 0001_esquema_inicial
Create Date: 2026-08-01

Agrega a la tabla `esmeraldas` (creada en 0001) las columnas de
`AuditoriaMixin` y `VersionadoMixin` (Etapa 7.5), completando la
entidad `Esmeralda` bajo el nuevo régimen obligatorio (ADR-008-01,
ADR-008-02):

- `actualizado_en` (NOT NULL, default `now()`)
- `creado_por`, `actualizado_por`, `eliminado_por` (FK a `usuarios.id`, nullable)
- `eliminado_en` (nullable)
- `version` (NOT NULL, default `1`)

100% ADITIVA: no elimina, renombra ni cambia el tipo de ninguna
columna existente. Todas las columnas nuevas son NULL-able o tienen
`server_default`, por lo que las filas ya existentes (ej. las sembradas
por `seed_db.py` en la Etapa 5) quedan válidas sin necesidad de
backfill manual.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002_completar_esmeraldas"
down_revision: str | None = "0001_esquema_inicial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "esmeraldas",
        sa.Column(
            "actualizado_en",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.add_column("esmeraldas", sa.Column("creado_por", sa.String(36), nullable=True))
    op.add_column("esmeraldas", sa.Column("actualizado_por", sa.String(36), nullable=True))
    op.add_column("esmeraldas", sa.Column("eliminado_en", sa.DateTime(timezone=True), nullable=True))
    op.add_column("esmeraldas", sa.Column("eliminado_por", sa.String(36), nullable=True))
    op.add_column(
        "esmeraldas",
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )

    op.create_foreign_key(
        "fk_esmeraldas_creado_por_usuarios",
        "esmeraldas",
        "usuarios",
        ["creado_por"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_esmeraldas_actualizado_por_usuarios",
        "esmeraldas",
        "usuarios",
        ["actualizado_por"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_esmeraldas_eliminado_por_usuarios",
        "esmeraldas",
        "usuarios",
        ["eliminado_por"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_esmeraldas_eliminado_por_usuarios", "esmeraldas", type_="foreignkey")
    op.drop_constraint("fk_esmeraldas_actualizado_por_usuarios", "esmeraldas", type_="foreignkey")
    op.drop_constraint("fk_esmeraldas_creado_por_usuarios", "esmeraldas", type_="foreignkey")

    op.drop_column("esmeraldas", "version")
    op.drop_column("esmeraldas", "eliminado_por")
    op.drop_column("esmeraldas", "eliminado_en")
    op.drop_column("esmeraldas", "actualizado_por")
    op.drop_column("esmeraldas", "creado_por")
    op.drop_column("esmeraldas", "actualizado_en")
