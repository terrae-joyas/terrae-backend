"""activos multimedia y completar certificados — Etapa 10

Revision ID: 0004_activos_multimedia
Revises: 0003_completar_inventario
Create Date: 2026-08-03

Tres cambios (ver ADR-010-01, ADR-010-02):

1. Elimina la tabla `fotografias` (Etapa 5, sin consumidores nunca
   construidos — verificado por búsqueda exhaustiva antes de esta
   etapa) y crea `activos_multimedia`, entidad polimórfica que la
   sustituye con alcance más amplio (fotos, imágenes microscópicas,
   certificados escaneados, recursos visuales) y metadatos completos
   de trazabilidad.
2. Completa `certificados` con `actualizado_en`, `actualizado_por`,
   `eliminado_en`, `eliminado_por`, `version` — sin tocar
   `emitido_en`/`emitido_por` (ya existían desde 0001, se conservan
   como campos de dominio propios, ADR-010-02).

100% aditiva salvo el `DROP TABLE fotografias`, justificado porque la
tabla nunca tuvo consumidores ni pudo tener filas reales (ningún
servicio la escribió jamás desde la Etapa 5).
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0004_activos_multimedia"
down_revision: str | None = "0003_completar_inventario"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- 1. Eliminar fotografias (sin consumidores, ver ADR-010-01) ---
    op.drop_table("fotografias")

    # --- 2. Crear activos_multimedia ---
    op.create_table(
        "activos_multimedia",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("entidad_tipo", sa.String(60), nullable=False),
        sa.Column("entidad_id", sa.String(36), nullable=False),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("hash_sha256", sa.String(64), nullable=False),
        sa.Column("dispositivo", sa.String(120), nullable=True),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "actualizado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("creado_por", sa.String(36), nullable=True),
        sa.Column("actualizado_por", sa.String(36), nullable=True),
        sa.Column("eliminado_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("eliminado_por", sa.String(36), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id", name="pk_activos_multimedia"),
        sa.ForeignKeyConstraint(
            ["creado_por"], ["usuarios.id"], name="fk_activos_multimedia_creado_por_usuarios", ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["actualizado_por"],
            ["usuarios.id"],
            name="fk_activos_multimedia_actualizado_por_usuarios",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["eliminado_por"],
            ["usuarios.id"],
            name="fk_activos_multimedia_eliminado_por_usuarios",
            ondelete="SET NULL",
        ),
    )
    op.create_index("ix_activos_multimedia_entidad_tipo", "activos_multimedia", ["entidad_tipo"])
    op.create_index("ix_activos_multimedia_entidad_id", "activos_multimedia", ["entidad_id"])

    # --- 3. Completar certificados (ADR-010-02) ---
    op.add_column(
        "certificados",
        sa.Column(
            "actualizado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.add_column("certificados", sa.Column("actualizado_por", sa.String(36), nullable=True))
    op.add_column("certificados", sa.Column("eliminado_en", sa.DateTime(timezone=True), nullable=True))
    op.add_column("certificados", sa.Column("eliminado_por", sa.String(36), nullable=True))
    op.add_column(
        "certificados",
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )

    op.create_foreign_key(
        "fk_certificados_actualizado_por_usuarios",
        "certificados",
        "usuarios",
        ["actualizado_por"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_certificados_eliminado_por_usuarios",
        "certificados",
        "usuarios",
        ["eliminado_por"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    # --- Revertir certificados ---
    op.drop_constraint("fk_certificados_eliminado_por_usuarios", "certificados", type_="foreignkey")
    op.drop_constraint("fk_certificados_actualizado_por_usuarios", "certificados", type_="foreignkey")
    op.drop_column("certificados", "version")
    op.drop_column("certificados", "eliminado_por")
    op.drop_column("certificados", "eliminado_en")
    op.drop_column("certificados", "actualizado_por")
    op.drop_column("certificados", "actualizado_en")

    # --- Revertir activos_multimedia ---
    op.drop_index("ix_activos_multimedia_entidad_id", table_name="activos_multimedia")
    op.drop_index("ix_activos_multimedia_entidad_tipo", table_name="activos_multimedia")
    op.drop_table("activos_multimedia")

    # --- Recrear fotografias (exactamente como en 0001) ---
    op.create_table(
        "fotografias",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("joya_id", sa.String(36), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("tipo", sa.String(30), nullable=False, server_default="catalogo"),
        sa.Column("orden", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_fotografias"),
        sa.ForeignKeyConstraint(
            ["joya_id"], ["joyas.id"], name="fk_fotografias_joya_id_joyas", ondelete="CASCADE"
        ),
    )
