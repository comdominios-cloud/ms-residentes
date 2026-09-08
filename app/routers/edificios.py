"""Catalogo de edificios. Lectura publica."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Edificio
from app.schemas import EdificioOut

router = APIRouter(prefix="/edificios", tags=["edificios"])


@router.get("", response_model=list[EdificioOut])
def listar(db: Session = Depends(get_db)) -> list[Edificio]:
    return list(db.scalars(select(Edificio).order_by(Edificio.id)))


@router.get("/{edificio_id}", response_model=EdificioOut)
def obtener(edificio_id: int, db: Session = Depends(get_db)) -> Edificio:
    edificio = db.get(Edificio, edificio_id)
    if edificio is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No existe el edificio {edificio_id}")
    return edificio
