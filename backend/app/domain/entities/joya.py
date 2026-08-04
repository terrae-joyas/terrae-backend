"""Entidad de dominio: Joya — pieza terminada de alta joyería.

Incluye la máquina de estados del ciclo de vida comercial de una pieza.
La transición a `VENDIDA` está deliberadamente excluida de las
transiciones permitidas por este módulo: solo el módulo de Ventas
(Etapa 19), que crea el registro `VentaModel` correspondiente, puede
marcar una joya como vendida. Permitirlo aquí crearía joyas "vendidas"
sin una venta real detrás.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class TipoJoya(str, Enum):
    ANILLO = "anillo"
    COLLAR = "collar"
    ARETES = "aretes"
    PULSERA = "pulsera"
    OTRO = "otro"


class EstadoJoya(str, Enum):
    EN_TALLER = "en_taller"
    DISPONIBLE = "disponible"
    RESERVADA = "reservada"
    VENDIDA = "vendida"
    EN_REPARACION = "en_reparacion"
    DADA_DE_BAJA = "dada_de_baja"


# Transiciones alcanzables desde este servicio (sin pasar por Ventas).
# VENDIDA nunca aparece como destino: solo la Etapa 19 puede llegar ahí.
TRANSICIONES_VALIDAS: dict[EstadoJoya, set[EstadoJoya]] = {
    EstadoJoya.EN_TALLER: {EstadoJoya.DISPONIBLE, EstadoJoya.DADA_DE_BAJA},
    EstadoJoya.DISPONIBLE: {EstadoJoya.RESERVADA, EstadoJoya.EN_REPARACION, EstadoJoya.EN_TALLER, EstadoJoya.DADA_DE_BAJA},
    EstadoJoya.RESERVADA: {EstadoJoya.DISPONIBLE, EstadoJoya.EN_REPARACION},
    EstadoJoya.EN_REPARACION: {EstadoJoya.DISPONIBLE, EstadoJoya.EN_TALLER},
    EstadoJoya.VENDIDA: set(),  # terminal desde este módulo
    EstadoJoya.DADA_DE_BAJA: set(),  # terminal
}


@dataclass
class Joya:
    referencia: str
    nombre: str
    tipo: TipoJoya
    material_metal: str | None = None
    estado: EstadoJoya = EstadoJoya.EN_TALLER
    esmeralda_id: str | None = None
    sucursal_id: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    creado_en: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def puede_transicionar_a(self, nuevo_estado: EstadoJoya) -> bool:
        return nuevo_estado in TRANSICIONES_VALIDAS.get(self.estado, set())
