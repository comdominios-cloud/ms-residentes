"""Tabla `usuarios`: cuentas de acceso al sistema.

Nunca guarda la password: solo su hash bcrypt.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    # NULL para el administrador, que no vive en ninguna unidad.
    residente_id: Mapped[int | None] = mapped_column(ForeignKey("residentes.id"))
    email: Mapped[str] = mapped_column(String(160), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(20), nullable=False, default="RESIDENTE")
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    ultimo_login: Mapped[datetime | None] = mapped_column(DateTime)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    residente: Mapped["Residente | None"] = relationship(back_populates="usuarios")
