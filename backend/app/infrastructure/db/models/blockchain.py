"""Modelos ORM: registro en blockchain (EmeraldChain / Polygon), NFT y QR."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class RegistroBlockchainModel(Base):
    """Constancia de registro on-chain de un certificado.

    `red` distingue Polygon Amoy Testnet de Polygon Mainnet; `modo`
    distingue una transacción real de una simulada (ver
    `BLOCKCHAIN_GATEWAY_MODE` en la configuración, Etapa 12).
    """

    __tablename__ = "registros_blockchain"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    certificado_id: Mapped[str] = mapped_column(
        ForeignKey("certificados.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    red: Mapped[str] = mapped_column(String(40), nullable=False, default="polygon-amoy")
    modo: Mapped[str] = mapped_column(String(20), nullable=False, default="simulado")
    tx_hash: Mapped[str | None] = mapped_column(String(80), nullable=True)
    numero_bloque: Mapped[int | None] = mapped_column(Integer, nullable=True)
    contrato_direccion: Mapped[str | None] = mapped_column(String(80), nullable=True)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="confirmado")
    registrado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    certificado = relationship("CertificadoModel", back_populates="registro_blockchain")
    nft: Mapped["NFTModel | None"] = relationship(back_populates="registro_blockchain", uselist=False)


class NFTModel(Base):
    """Token no fungible asociado a un certificado (representación digital
    de propiedad/autenticidad, Etapa 20)."""

    __tablename__ = "nfts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    registro_blockchain_id: Mapped[str] = mapped_column(
        ForeignKey("registros_blockchain.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    token_id: Mapped[str] = mapped_column(String(80), nullable=False)
    contrato_direccion: Mapped[str] = mapped_column(String(80), nullable=False)
    wallet_propietario: Mapped[str | None] = mapped_column(String(80), nullable=True)
    metadata_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)  # IPFS/Pinata
    acunado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    registro_blockchain: Mapped[RegistroBlockchainModel] = relationship(back_populates="nft")


class TokenBlockchainModel(Base):
    """Tokens fungibles asociados a una wallet (distinto de un NFT, que es
    no-fungible). Pensado para futuros programas de fidelización o
    fraccionamiento de valor sobre certificados, sin acoplarse a un caso
    de uso específico todavía (se define en la Etapa 20)."""

    __tablename__ = "tokens_blockchain"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    wallet_direccion: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    contrato_direccion: Mapped[str] = mapped_column(String(80), nullable=False)
    simbolo: Mapped[str] = mapped_column(String(20), nullable=False)
    cantidad: Mapped[str] = mapped_column(String(80), nullable=False, default="0")
    # se almacena como string para no perder precisión con enteros grandes (wei)
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    """Código QR de trazabilidad impreso/embebido junto a la joya (Etapa 11)."""

    __tablename__ = "qr_codigos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    certificado_id: Mapped[str] = mapped_column(
        ForeignKey("certificados.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    url_publica: Mapped[str] = mapped_column(String(500), nullable=False)
    hash_verificacion: Mapped[str] = mapped_column(String(64), nullable=False)
    generado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    certificado = relationship("CertificadoModel", back_populates="qr")
