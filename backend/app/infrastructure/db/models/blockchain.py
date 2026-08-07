[12:32 a.m., 7/8/2026] Juan S: ==================================== ERRORS ====================================
____ ERROR collecting backend/app/tests/test_auditoria_infra.py ____
ImportError while importing test module '/home/runner/work/terrae-backend/terrae-backend/backend/app/tests/test_auditoria_infra.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/opt/hostedtoolcache/Python/3.12.13/x64/lib/python3.12/importlib/_init_.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/app/tests/test_auditoria_infra.py:18: in <module>
    import app.infrastructure.db.models  # noqa: F401
backend/app/infrastructure/db/models/_init_.py:17: in <module>
    from app.infrastructure.db.models.blockchain import (
backend/app/i…
[12:34 a.m., 7/8/2026] Juan S: """Modelos ORM: registro en blockchain (EmeraldChain / Polygon), NFT y QR."""

from _future_ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class RegistroBlockchainModel(Base):
    """Constancia de registro on-chain de un certificado."""

    _tablename_ = "registros_blockchain"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    certificado_id: Mapped[str] = mapped_column(
        ForeignKey("certificados.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    red: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="polygon-amoy",
    )

    modo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="simulado",
    )

    tx_hash: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )

    numero_bloque: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    contrato_direccion: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="confirmado",
    )

    registrado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    certificado = relationship(
        "CertificadoModel",
        back_populates="registro_blockchain",
    )

    nft: Mapped["NFTModel | None"] = relationship(
        back_populates="registro_blockchain",
        uselist=False,
    )


class NFTModel(Base):
    """Token no fungible asociado a un certificado."""

    _tablename_ = "nfts"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    registro_blockchain_id: Mapped[str] = mapped_column(
        ForeignKey("registros_blockchain.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    token_id: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    contrato_direccion: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    wallet_propietario: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )

    metadata_uri: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    acunado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    registro_blockchain: Mapped[RegistroBlockchainModel] = relationship(
        back_populates="nft",
    )


class TokenBlockchainModel(Base):
    """Tokens fungibles asociados a una wallet."""

    _tablename_ = "tokens_blockchain"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    wallet_direccion: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        index=True,
    )

    contrato_direccion: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    simbolo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    cantidad: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        default="0",
    )

    # Se almacena como string para no perder precisión
    # con enteros grandes (wei).
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class QRModel(Base):
    """Código QR de trazabilidad asociado a un certificado."""

    _tablename_ = "qr_codigos"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    certificado_id: Mapped[str] = mapped_column(
        ForeignKey("certificados.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    url_publica: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    hash_verificacion: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    generado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    certificado = relationship(
        "CertificadoModel",
        back_populates="qr",
    )
