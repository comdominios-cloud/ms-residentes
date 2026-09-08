"""Contratos HTTP de edificios."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EdificioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    direccion: str
    num_pisos: int
    creado_en: datetime
