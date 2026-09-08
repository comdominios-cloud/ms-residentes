"""Tabla `unidades`: los departamentos de cada edificio."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Unidad(Base):
    __tablename__ = "unidades"

    id: Mapped[int] = mapped_column(primary_key=True)
    edificio_id: Mapped[int] = mapped_column(ForeignKey("edificios.id"), nullable=False)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False)
    piso: Mapped[int] = mapped_column(Integer, nullable=False)
    area_m2: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    edificio: Mapped["Edificio"] = relationship(back_populates="unidades")
    residentes: Mapped[list["Residente"]] = relationship(back_populates="unidad")
