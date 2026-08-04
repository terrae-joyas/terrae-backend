"""completar inventario: auditoria y version — Etapa 9

Revision ID: 0003_completar_inventario
Revises: 0002_completar_esmeraldas
Create Date: 2026-08-02

Agrega a la tabla `inventario` (creada en 0001) las columnas de
`AuditoriaMixin` y `VersionadoMixin` (Etapa 7.5) que todavía faltaban
(`actualizado_en` ya existía desde 0001 — ver ADR-009-02):

- `creado_en` (NOT NULL, default `now()`)
- `creado_por`, `actualizado_por`, `eliminado_por` (FK a `usuarios.id`, nullable)
- `eliminado_en` (nullable)
- `version` (NOT NULL, default `1`)

100% ADITIVA, mismo patrón que 0002_completar_esmeraldas: no elimina,
renombra ni cambia el tipo de ninguna columna existente.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003_completar_inventario"
down_revision: str | None = "0002_completar_esmeraldas"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "inventario",
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.add_column("inventario", sa.Column("creado_por", sa.String(36), nullable=True))
    op.add_column("inventario", sa.Column("actualizado_por", sa.String(36), nullable=True))
    op.add_column("inventario", sa.Column("eliminado_en", sa.DateTime(timezone=True), nullable=True))
    op.add_column("inventario", sa.Column("eliminado_por", sa.String(36), nullable=True))
    op.add_column(
        "inventario",
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )

    op.create_foreign_key(
        "fk_inventario_creado_por_usuarios",
        "inventario",
        "usuarios",
        ["creado_por"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_inventario_actualizado_por_usuarios",
        "inventario",
        "usuarios",
        ["actualizado_por"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_inventario_eliminado_por_usuarios",
        "inventario",
        "usuarios",
        ["eliminado_por"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_inventario_eliminado_por_usuarios", "inventario", type_="foreignkey")
    op.drop_constraint("fk_inventario_actualizado_por_usuarios", "inventario", type_="foreignkey")
    op.drop_constraint("fk_inventario_creado_por_usuarios", "inventario", type_="foreignkey")

    op.drop_column("inventario", "version")
    op.drop_column("inventario", "eliminado_por")
    op.drop_column("inventario", "eliminado_en")
    op.drop_column("inventario", "actualizado_por")
    op.drop_column("inventario", "creado_por")
    op.drop_column("inventario", "creado_en")
