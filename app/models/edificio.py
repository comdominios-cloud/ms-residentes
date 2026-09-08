"""Tabla `edificios`: las torres del condominio."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Edificio(Base):
    __tablename__ = "edificios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    direccion: Mapped[str] = mapped_column(String(255), nullable=False)
    num_pisos: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Un edificio tiene muchas unidades.
    unidades: Mapped[list["Unidad"]] = relationship(back_populates="edificio")
