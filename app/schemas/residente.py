"""Contratos HTTP de residentes.

Entrada y salida son schemas distintos a proposito:
- `ResidenteCreate` es lo que el cliente puede mandar (sin id ni fechas).
- `ResidenteOut` es lo que devolvemos.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.unidad import UnidadOut


class ResidenteBase(BaseModel):
    nombres: str = Field(min_length=1, max_length=120)
    apellidos: str = Field(min_length=1, max_length=120)
    documento: str = Field(min_length=8, max_length=20)
    email: EmailStr | None = None
    telefono: str | None = Field(default=None, max_length=30)
    tipo: Literal["PROPIETARIO", "INQUILINO"] = "PROPIETARIO"


class ResidenteCreate(ResidenteBase):
    unidad_id: int


class ResidenteUpdate(BaseModel):
    """Todo opcional: se actualiza solo lo que venga."""

    nombres: str | None = Field(default=None, min_length=1, max_length=120)
    apellidos: str | None = Field(default=None, min_length=1, max_length=120)
    email: EmailStr | None = None
    telefono: str | None = Field(default=None, max_length=30)
    tipo: Literal["PROPIETARIO", "INQUILINO"] | None = None
    activo: bool | None = None


class ResidenteOut(ResidenteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    unidad_id: int
    activo: bool
    creado_en: datetime


class ResidenteDetalle(ResidenteOut):
    """Residente con su unidad incluida, para no obligar a un segundo request."""

    unidad: UnidadOut | None = None
