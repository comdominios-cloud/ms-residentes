from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.edificio import EdificioOut
from app.schemas.residente import (
    ResidenteCreate,
    ResidenteDetalle,
    ResidenteOut,
    ResidenteUpdate,
)
from app.schemas.unidad import UnidadDetalle, UnidadOut
from app.schemas.usuario import UsuarioCreate, UsuarioOut

__all__ = [
    "LoginRequest",
    "RegisterRequest",
    "TokenResponse",
    "EdificioOut",
    "ResidenteCreate",
    "ResidenteDetalle",
    "ResidenteOut",
    "ResidenteUpdate",
    "UnidadDetalle",
    "UnidadOut",
    "UsuarioCreate",
    "UsuarioOut",
]
