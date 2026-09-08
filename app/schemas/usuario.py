"""Contratos HTTP de usuarios.

`UsuarioOut` NO incluye `password_hash`: FastAPI valida la respuesta contra
este schema, asi que el hash no puede filtrarse por descuido.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)  # bcrypt corta en 72 bytes
    residente_id: int | None = None
    rol: Literal["ADMIN", "RESIDENTE"] = "RESIDENTE"


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    rol: str
    residente_id: int | None
    activo: bool
    ultimo_login: datetime | None
    creado_en: datetime
