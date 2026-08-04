"""
Script de siembra de datos de referencia (desarrollo local).

Ejecutar tras aplicar las migraciones:

    docker compose exec backend python -m app.scripts.seed_db

Crea:
- 4 usuarios de demostración (uno por rol) — ya se siembran también
  automáticamente al arrancar la API (ver app/dependencies.py); este
  script es idempotente, así que ejecutarlo de nuevo no duplica nada.
- 1 sucursal de referencia (Taller Bogotá).
- 2 esmeraldas canónicas de referencia (Muzo y Chivor).
- 2 joyas de referencia asociadas a esas esmeraldas.

No crea certificados, blockchain, ventas, etc. — esas entidades se
poblarán con datos reales a partir de las etapas de dominio (7 en
adelante), cuando existan los servicios de aplicación correspondientes.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.config import get_settings
from app.dependencies import get_usuario_repository
from app.infrastructure.db.models.gemologia import EsmeraldaModel, JoyaModel
from app.infrastructure.db.models.organizacion import SucursalModel
from app.infrastructure.db.session import get_session_factory


def sembrar_organizacion_y_gemologia() -> None:
    session_factory = get_session_factory()
    with session_factory() as session:
        sucursal = session.query(SucursalModel).filter_by(nombre="Taller Bogotá").one_or_none()
        if sucursal is None:
            sucursal = SucursalModel(
                id=str(uuid.uuid4()),
                nombre="Taller Bogotá",
                tipo="taller",
                ciudad="Bogotá",
                direccion="Zona Industrial, Bogotá D.C.",
                activa=True,
            )
            session.add(sucursal)
            session.flush()
            print(f"✅ Sucursal creada: {sucursal.nombre} ({sucursal.id})")
        else:
            print(f"ℹ️  Sucursal ya existe: {sucursal.nombre}")

        esmeraldas_referencia = [
            {
                "codigo_interno": "ESM-MUZO-0001",
                "mina_origen": "Muzo",
                "quilates": 2.35,
                "color": "Verde intenso vívido",
                "claridad": "VS (ligeras inclusiones visibles a 10x)",
                "corte": "Esmeralda (step cut)",
                "tratamientos": "Aceite de cedro (tratamiento menor, estándar de la industria)",
                "tipo_inclusion_principal": "Inclusión trifásica (three-phase)",
            },
            {
                "codigo_interno": "ESM-CHIVOR-0001",
                "mina_origen": "Chivor",
                "quilates": 1.82,
                "color": "Verde azulado brillante",
                "claridad": "VVS (inclusiones mínimas)",
                "corte": "Ovalada",
                "tratamientos": "Ninguno detectado",
                "tipo_inclusion_principal": "Inclusión trifásica (three-phase)",
            },
        ]

        joyas_referencia = [
            {
                "referencia": "TR-2026-00842",
                "nombre": "Anillo Solitario Muzo",
                "tipo": "anillo",
                "material_metal": "Oro blanco 18k",
                "codigo_esmeralda": "ESM-MUZO-0001",
            },
            {
                "referencia": "TR-2026-00843",
                "nombre": "Aretes Gota Chivor",
                "tipo": "aretes",
                "material_metal": "Oro amarillo 18k",
                "codigo_esmeralda": "ESM-CHIVOR-0001",
            },
        ]

        esmeraldas_por_codigo: dict[str, EsmeraldaModel] = {}
        for datos in esmeraldas_referencia:
            existente = (
                session.query(EsmeraldaModel)
                .filter_by(codigo_interno=datos["codigo_interno"])
                .one_or_none()
            )
            if existente:
                esmeraldas_por_codigo[datos["codigo_interno"]] = existente
                print(f"ℹ️  Esmeralda ya existe: {datos['codigo_interno']}")
                continue
            esmeralda = EsmeraldaModel(id=str(uuid.uuid4()), **datos)
            session.add(esmeralda)
            session.flush()
            esmeraldas_por_codigo[datos["codigo_interno"]] = esmeralda
            print(f"✅ Esmeralda creada: {esmeralda.codigo_interno} ({esmeralda.mina_origen})")

        for datos in joyas_referencia:
            existente = session.query(JoyaModel).filter_by(referencia=datos["referencia"]).one_or_none()
            if existente:
                print(f"ℹ️  Joya ya existe: {datos['referencia']}")
                continue
            esmeralda = esmeraldas_por_codigo[datos.pop("codigo_esmeralda")]
            joya = JoyaModel(
                id=str(uuid.uuid4()),
                referencia=datos["referencia"],
                nombre=datos["nombre"],
                tipo=datos["tipo"],
                material_metal=datos["material_metal"],
                estado="en_taller",
                esmeralda_id=esmeralda.id,
                sucursal_id=sucursal.id,
            )
            session.add(joya)
            print(f"✅ Joya creada: {joya.referencia} — {joya.nombre}")

        session.commit()


def main() -> None:
    settings = get_settings()
    if not settings.database_url:
        raise SystemExit(
            "DATABASE_URL no configurada. Este script requiere PostgreSQL "
            "(Etapa 5). Revisa .env o ejecuta dentro de docker compose."
        )

    print("🌱 Sembrando datos de referencia de Terrae...\n")

    # Usuarios: reutiliza la misma lógica idempotente que corre al
    # arrancar la API (ver app/dependencies.py::_sembrar_usuarios_demo).
    get_usuario_repository()
    print("✅ Usuarios de demostración verificados/creados (4 roles).\n")

    sembrar_organizacion_y_gemologia()

    print("\n🌱 Siembra completada.")


if __name__ == "__main__":
    main()
