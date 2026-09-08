"""Tabla `residentes`: las personas asociadas a una unidad."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Residente(Base):
    __tablename__ = "residentes"

    id: Mapped[int] = mapped_column(primary_key=True)
    unidad_id: Mapped[int] = mapped_column(ForeignKey("unidades.id"), nullable=False)
    nombres: Mapped[str] = mapped_column(String(120), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(120), nullable=False)
    documento: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    email: Mapped[str | None] = mapped_column(String(160))
    telefono: Mapped[str | None] = mapped_column(String(30))
    tipo: Mapped[str] = mapped_column(String(20), nullable=False, default="PROPIETARIO")
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    unidad: Mapped["Unidad"] = relationship(back_populates="residentes")
    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="residente")
