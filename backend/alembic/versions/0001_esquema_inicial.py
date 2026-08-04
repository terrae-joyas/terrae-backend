"""esquema inicial completo — Etapa 5

Revision ID: 0001_esquema_inicial
Revises:
Create Date: 2026-07-30

Crea las 24 tablas del modelo de datos inicial de Terrae: usuarios y
permisos, organización (sucursales), gemología (esmeraldas, joyas,
inventario), multimedia (fotografías), laboratorio SIEGEM Lab
(microscopios, calibraciones, capturas), certificación, blockchain
(registros, NFT, tokens, QR), comercial (clientes, historial de
propietarios, ventas, garantías, mantenimientos) y trazabilidad
transversal (auditorías, historial de eventos, logs de sistema).

Escrita a mano (no autogenerada) porque este entorno no tiene acceso a
una instancia real de PostgreSQL; se corresponde 1:1 con los modelos en
app/infrastructure/db/models/. Ver checklist de validación en
docs/ETAPA_5_BASE_DE_DATOS.md para confirmar la correspondencia antes de
aplicarla en un entorno real.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_esquema_inicial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- usuarios ---
    op.create_table(
        "usuarios",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("nombre_completo", sa.String(120), nullable=False),
        sa.Column("correo", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("rol", sa.String(20), nullable=False, server_default="cliente"),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_usuarios"),
        sa.UniqueConstraint("correo", name="uq_usuarios_correo"),
    )
    op.create_index("ix_usuarios_correo", "usuarios", ["correo"])

    # --- permisos ---
    op.create_table(
        "permisos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("codigo", sa.String(80), nullable=False),
        sa.Column("descripcion", sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_permisos"),
        sa.UniqueConstraint("codigo", name="uq_permisos_codigo"),
    )

    # --- rol_permisos ---
    op.create_table(
        "rol_permisos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("rol", sa.String(20), nullable=False),
        sa.Column("permiso_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_rol_permisos"),
        sa.ForeignKeyConstraint(
            ["permiso_id"], ["permisos.id"], name="fk_rol_permisos_permiso_id_permisos", ondelete="CASCADE"
        ),
    )
    op.create_index("ix_rol_permisos_rol", "rol_permisos", ["rol"])

    # --- sucursales ---
    op.create_table(
        "sucursales",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column("ciudad", sa.String(80), nullable=False),
        sa.Column("direccion", sa.String(255), nullable=True),
        sa.Column("activa", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_sucursales"),
    )

    # --- esmeraldas ---
    op.create_table(
        "esmeraldas",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("codigo_interno", sa.String(40), nullable=False),
        sa.Column("mina_origen", sa.String(40), nullable=False),
        sa.Column("quilates", sa.Float(), nullable=False),
        sa.Column("color", sa.String(60), nullable=True),
        sa.Column("claridad", sa.String(60), nullable=True),
        sa.Column("corte", sa.String(60), nullable=True),
        sa.Column("tratamientos", sa.String(255), nullable=True),
        sa.Column("tipo_inclusion_principal", sa.String(120), nullable=True),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_esmeraldas"),
        sa.UniqueConstraint("codigo_interno", name="uq_esmeraldas_codigo_interno"),
    )
    op.create_index("ix_esmeraldas_codigo_interno", "esmeraldas", ["codigo_interno"])

    # --- joyas ---
    op.create_table(
        "joyas",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("referencia", sa.String(40), nullable=False),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("tipo", sa.String(40), nullable=False),
        sa.Column("material_metal", sa.String(60), nullable=True),
        sa.Column("estado", sa.String(30), nullable=False, server_default="en_taller"),
        sa.Column("esmeralda_id", sa.String(36), nullable=True),
        sa.Column("sucursal_id", sa.String(36), nullable=True),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_joyas"),
        sa.UniqueConstraint("referencia", name="uq_joyas_referencia"),
        sa.ForeignKeyConstraint(
            ["esmeralda_id"], ["esmeraldas.id"], name="fk_joyas_esmeralda_id_esmeraldas", ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["sucursal_id"], ["sucursales.id"], name="fk_joyas_sucursal_id_sucursales", ondelete="SET NULL"
        ),
    )
    op.create_index("ix_joyas_referencia", "joyas", ["referencia"])

    # --- inventario ---
    op.create_table(
        "inventario",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("joya_id", sa.String(36), nullable=False),
        sa.Column("sucursal_id", sa.String(36), nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("ubicacion_fisica", sa.String(120), nullable=True),
        sa.Column(
            "actualizado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id", name="pk_inventario"),
        sa.UniqueConstraint("joya_id", name="uq_inventario_joya_id"),
        sa.ForeignKeyConstraint(
            ["joya_id"], ["joyas.id"], name="fk_inventario_joya_id_joyas", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["sucursal_id"], ["sucursales.id"], name="fk_inventario_sucursal_id_sucursales", ondelete="RESTRICT"
        ),
    )

    # --- fotografias ---
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

    # --- microscopios ---
    op.create_table(
        "microscopios",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("codigo_equipo", sa.String(40), nullable=False),
        sa.Column("modelo", sa.String(120), nullable=False),
        sa.Column("sucursal_id", sa.String(36), nullable=True),
        sa.Column("en_servicio", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("id", name="pk_microscopios"),
        sa.UniqueConstraint("codigo_equipo", name="uq_microscopios_codigo_equipo"),
        sa.ForeignKeyConstraint(
            ["sucursal_id"], ["sucursales.id"], name="fk_microscopios_sucursal_id_sucursales", ondelete="SET NULL"
        ),
    )

    # --- calibraciones ---
    op.create_table(
        "calibraciones",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("microscopio_id", sa.String(36), nullable=False),
        sa.Column("fecha_calibracion", sa.DateTime(timezone=True), nullable=False),
        sa.Column("responsable", sa.String(120), nullable=False),
        sa.Column("resultado", sa.String(30), nullable=False, server_default="aprobada"),
        sa.Column("observaciones", sa.String(500), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_calibraciones"),
        sa.ForeignKeyConstraint(
            ["microscopio_id"],
            ["microscopios.id"],
            name="fk_calibraciones_microscopio_id_microscopios",
            ondelete="CASCADE",
        ),
    )

    # --- capturas ---
    op.create_table(
        "capturas",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("esmeralda_id", sa.String(36), nullable=True),
        sa.Column("microscopio_id", sa.String(36), nullable=True),
        sa.Column("imagen_url", sa.String(500), nullable=False),
        sa.Column("aumento_x", sa.Float(), nullable=True),
        sa.Column("modelo_ia_usado", sa.String(80), nullable=True),
        sa.Column("resultado_json", sa.String(), nullable=True),
        sa.Column("capturado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_capturas"),
        sa.ForeignKeyConstraint(
            ["esmeralda_id"], ["esmeraldas.id"], name="fk_capturas_esmeralda_id_esmeraldas", ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["microscopio_id"],
            ["microscopios.id"],
            name="fk_capturas_microscopio_id_microscopios",
            ondelete="SET NULL",
        ),
    )

    # --- certificados ---
    op.create_table(
        "certificados",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("numero_certificado", sa.String(40), nullable=False),
        sa.Column("joya_id", sa.String(36), nullable=False),
        sa.Column("hash_sha256", sa.String(64), nullable=False),
        sa.Column("emitido_por", sa.String(36), nullable=True),
        sa.Column("estado", sa.String(30), nullable=False, server_default="emitido"),
        sa.Column("emitido_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_certificados"),
        sa.UniqueConstraint("numero_certificado", name="uq_certificados_numero_certificado"),
        sa.UniqueConstraint("hash_sha256", name="uq_certificados_hash_sha256"),
        sa.ForeignKeyConstraint(
            ["joya_id"], ["joyas.id"], name="fk_certificados_joya_id_joyas", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["emitido_por"], ["usuarios.id"], name="fk_certificados_emitido_por_usuarios", ondelete="SET NULL"
        ),
    )
    op.create_index("ix_certificados_numero_certificado", "certificados", ["numero_certificado"])

    # --- registros_blockchain ---
    op.create_table(
        "registros_blockchain",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("certificado_id", sa.String(36), nullable=False),
        sa.Column("red", sa.String(40), nullable=False, server_default="polygon-amoy"),
        sa.Column("modo", sa.String(20), nullable=False, server_default="simulado"),
        sa.Column("tx_hash", sa.String(80), nullable=True),
        sa.Column("numero_bloque", sa.Integer(), nullable=True),
        sa.Column("contrato_direccion", sa.String(80), nullable=True),
        sa.Column("estado", sa.String(30), nullable=False, server_default="confirmado"),
        sa.Column("registrado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_registros_blockchain"),
        sa.UniqueConstraint("certificado_id", name="uq_registros_blockchain_certificado_id"),
        sa.ForeignKeyConstraint(
            ["certificado_id"],
            ["certificados.id"],
            name="fk_registros_blockchain_certificado_id_certificados",
            ondelete="CASCADE",
        ),
    )

    # --- nfts ---
    op.create_table(
        "nfts",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("registro_blockchain_id", sa.String(36), nullable=False),
        sa.Column("token_id", sa.String(80), nullable=False),
        sa.Column("contrato_direccion", sa.String(80), nullable=False),
        sa.Column("wallet_propietario", sa.String(80), nullable=True),
        sa.Column("metadata_uri", sa.String(500), nullable=True),
        sa.Column("acunado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_nfts"),
        sa.UniqueConstraint("registro_blockchain_id", name="uq_nfts_registro_blockchain_id"),
        sa.ForeignKeyConstraint(
            ["registro_blockchain_id"],
            ["registros_blockchain.id"],
            name="fk_nfts_registro_blockchain_id_registros_blockchain",
            ondelete="CASCADE",
        ),
    )

    # --- tokens_blockchain ---
    op.create_table(
        "tokens_blockchain",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("wallet_direccion", sa.String(80), nullable=False),
        sa.Column("contrato_direccion", sa.String(80), nullable=False),
        sa.Column("simbolo", sa.String(20), nullable=False),
        sa.Column("cantidad", sa.String(80), nullable=False, server_default="0"),
        sa.Column(
            "actualizado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id", name="pk_tokens_blockchain"),
    )
    op.create_index("ix_tokens_blockchain_wallet_direccion", "tokens_blockchain", ["wallet_direccion"])

    # --- qr_codigos ---
    op.create_table(
        "qr_codigos",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("certificado_id", sa.String(36), nullable=False),
        sa.Column("url_publica", sa.String(500), nullable=False),
        sa.Column("hash_verificacion", sa.String(64), nullable=False),
        sa.Column("generado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_qr_codigos"),
        sa.UniqueConstraint("certificado_id", name="uq_qr_codigos_certificado_id"),
        sa.ForeignKeyConstraint(
            ["certificado_id"],
            ["certificados.id"],
            name="fk_qr_codigos_certificado_id_certificados",
            ondelete="CASCADE",
        ),
    )

    # --- clientes ---
    op.create_table(
        "clientes",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("usuario_id", sa.String(36), nullable=True),
        sa.Column("nombre_completo", sa.String(120), nullable=False),
        sa.Column("correo_contacto", sa.String(255), nullable=True),
        sa.Column("telefono_contacto", sa.String(30), nullable=True),
        sa.Column("documento_identidad", sa.String(40), nullable=True),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_clientes"),
        sa.UniqueConstraint("usuario_id", name="uq_clientes_usuario_id"),
        sa.ForeignKeyConstraint(
            ["usuario_id"], ["usuarios.id"], name="fk_clientes_usuario_id_usuarios", ondelete="SET NULL"
        ),
    )

    # --- historial_propietarios ---
    op.create_table(
        "historial_propietarios",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("joya_id", sa.String(36), nullable=False),
        sa.Column("cliente_id", sa.String(36), nullable=True),
        sa.Column("nombre_propietario", sa.String(120), nullable=False),
        sa.Column("fecha_inicio", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_fin", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_historial_propietarios"),
        sa.ForeignKeyConstraint(
            ["joya_id"], ["joyas.id"], name="fk_historial_propietarios_joya_id_joyas", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["cliente_id"],
            ["clientes.id"],
            name="fk_historial_propietarios_cliente_id_clientes",
            ondelete="SET NULL",
        ),
    )

    # --- ventas ---
    op.create_table(
        "ventas",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("joya_id", sa.String(36), nullable=False),
        sa.Column("cliente_id", sa.String(36), nullable=False),
        sa.Column("sucursal_id", sa.String(36), nullable=True),
        sa.Column("precio", sa.Float(), nullable=False),
        sa.Column("moneda", sa.String(10), nullable=False, server_default="COP"),
        sa.Column("fecha_venta", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_ventas"),
        sa.ForeignKeyConstraint(
            ["joya_id"], ["joyas.id"], name="fk_ventas_joya_id_joyas", ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["cliente_id"], ["clientes.id"], name="fk_ventas_cliente_id_clientes", ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["sucursal_id"], ["sucursales.id"], name="fk_ventas_sucursal_id_sucursales", ondelete="SET NULL"
        ),
    )

    # --- garantias ---
    op.create_table(
        "garantias",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("venta_id", sa.String(36), nullable=False),
        sa.Column("fecha_inicio", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_fin", sa.DateTime(timezone=True), nullable=False),
        sa.Column("condiciones", sa.String(1000), nullable=True),
        sa.Column("estado", sa.String(20), nullable=False, server_default="vigente"),
        sa.PrimaryKeyConstraint("id", name="pk_garantias"),
        sa.UniqueConstraint("venta_id", name="uq_garantias_venta_id"),
        sa.ForeignKeyConstraint(
            ["venta_id"], ["ventas.id"], name="fk_garantias_venta_id_ventas", ondelete="CASCADE"
        ),
    )

    # --- mantenimientos ---
    op.create_table(
        "mantenimientos",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("joya_id", sa.String(36), nullable=False),
        sa.Column("fecha", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("descripcion", sa.String(500), nullable=False),
        sa.Column("tecnico_responsable", sa.String(120), nullable=True),
        sa.Column("sucursal_id", sa.String(36), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_mantenimientos"),
        sa.ForeignKeyConstraint(
            ["joya_id"], ["joyas.id"], name="fk_mantenimientos_joya_id_joyas", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["sucursal_id"],
            ["sucursales.id"],
            name="fk_mantenimientos_sucursal_id_sucursales",
            ondelete="SET NULL",
        ),
    )

    # --- auditorias ---
    op.create_table(
        "auditorias",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("usuario_id", sa.String(36), nullable=True),
        sa.Column("accion", sa.String(120), nullable=False),
        sa.Column("entidad_tipo", sa.String(60), nullable=False),
        sa.Column("entidad_id", sa.String(36), nullable=True),
        sa.Column("ip_origen", sa.String(45), nullable=True),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_auditorias"),
        sa.ForeignKeyConstraint(
            ["usuario_id"], ["usuarios.id"], name="fk_auditorias_usuario_id_usuarios", ondelete="SET NULL"
        ),
    )

    # --- historial_eventos ---
    op.create_table(
        "historial_eventos",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("entidad_tipo", sa.String(60), nullable=False),
        sa.Column("entidad_id", sa.String(36), nullable=False),
        sa.Column("evento", sa.String(120), nullable=False),
        sa.Column("detalle", sa.String(1000), nullable=True),
        sa.Column("ocurrido_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_historial_eventos"),
    )
    op.create_index("ix_historial_eventos_entidad_id", "historial_eventos", ["entidad_id"])

    # --- logs_sistema ---
    op.create_table(
        "logs_sistema",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("nivel", sa.String(20), nullable=False, server_default="info"),
        sa.Column("origen", sa.String(80), nullable=False),
        sa.Column("mensaje", sa.String(2000), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_logs_sistema"),
    )


def downgrade() -> None:
    # Orden inverso al de creación, respetando dependencias de FK.
    op.drop_table("logs_sistema")
    op.drop_table("historial_eventos")
    op.drop_table("auditorias")
    op.drop_table("mantenimientos")
    op.drop_table("garantias")
    op.drop_table("ventas")
    op.drop_table("historial_propietarios")
    op.drop_table("clientes")
    op.drop_table("qr_codigos")
    op.drop_table("tokens_blockchain")
    op.drop_table("nfts")
    op.drop_table("registros_blockchain")
    op.drop_table("certificados")
    op.drop_table("capturas")
    op.drop_table("calibraciones")
    op.drop_table("microscopios")
    op.drop_table("fotografias")
    op.drop_table("inventario")
    op.drop_table("joyas")
    op.drop_table("esmeraldas")
    op.drop_table("sucursales")
    op.drop_table("rol_permisos")
    op.drop_table("permisos")
    op.drop_table("usuarios")
