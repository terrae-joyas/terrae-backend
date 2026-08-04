"""
Importa todos los modelos ORM para que:
1. Alembic (`env.py`) pueda detectarlos vía `Base.metadata` al generar
   migraciones.
2. Las relaciones declaradas como strings (ej. `relationship("JoyaModel")`)
   se resuelvan correctamente sin importar el orden de importación.

Cualquier modelo nuevo DEBE agregarse aquí para que la migración lo
incluya.
"""

from app.infrastructure.db.models.auditoria import (
    AuditoriaModel,
    HistorialEventoModel,
    LogSistemaModel,
)
from app.infrastructure.db.models.blockchain import (
    NFTModel,
    QRModel,
    RegistroBlockchainModel,
    TokenBlockchainModel,
)
from app.infrastructure.db.models.certificacion import CertificadoModel
from app.infrastructure.db.models.comercial import (
    ClienteModel,
    GarantiaModel,
    MantenimientoModel,
    PropietarioHistorialModel,
    VentaModel,
)
from app.infrastructure.db.models.gemologia import EsmeraldaModel, InventarioModel, JoyaModel
from app.infrastructure.db.models.laboratorio import (
    CalibracionModel,
    CapturaModel,
    MicroscopioModel,
)
from app.infrastructure.db.models.multimedia import ActivoMultimediaModel
from app.infrastructure.db.models.organizacion import SucursalModel
from app.infrastructure.db.models.usuarios import PermisoModel, RolPermisoModel, UsuarioModel

__all__ = [
    "UsuarioModel",
    "PermisoModel",
    "RolPermisoModel",
    "SucursalModel",
    "EsmeraldaModel",
    "JoyaModel",
    "InventarioModel",
    "ActivoMultimediaModel",
    "MicroscopioModel",
    "CalibracionModel",
    "CapturaModel",
    "CertificadoModel",
    "RegistroBlockchainModel",
    "NFTModel",
    "TokenBlockchainModel",
    "QRModel",
    "ClienteModel",
    "PropietarioHistorialModel",
    "VentaModel",
    "GarantiaModel",
    "MantenimientoModel",
    "AuditoriaModel",
    "HistorialEventoModel",
    "LogSistemaModel",
]
