"""Contratos HTTP de unidades."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.schemas.edificio import EdificioOut


class UnidadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    edificio_id: int
    codigo: str
    piso: int
    area_m2: Decimal
    creado_en: datetime


class UnidadDetalle(UnidadOut):
    """Unidad con el edificio al que pertenece."""

    edificio: EdificioOut | None = None
