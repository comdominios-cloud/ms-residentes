"""Importa todos los modelos para que SQLAlchemy resuelva las relaciones."""

from app.models.base import Base
from app.models.edificio import Edificio
from app.models.residente import Residente
from app.models.unidad import Unidad
from app.models.usuario import Usuario

__all__ = ["Base", "Edificio", "Unidad", "Residente", "Usuario"]
