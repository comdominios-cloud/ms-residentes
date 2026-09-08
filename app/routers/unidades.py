"""Unidades (departamentos). Lectura publica."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models import Unidad
from app.schemas import UnidadDetalle, UnidadOut

router = APIRouter(prefix="/unidades", tags=["unidades"])


@router.get("", response_model=list[UnidadOut])
def listar(
    edificio_id: int | None = Query(None, description="Filtra por edificio"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[Unidad]:
    stmt = select(Unidad).order_by(Unidad.id).limit(limit).offset(offset)
    if edificio_id is not None:
        stmt = stmt.where(Unidad.edificio_id == edificio_id)
    return list(db.scalars(stmt))


@router.get("/{unidad_id}", response_model=UnidadDetalle)
def obtener(unidad_id: int, db: Session = Depends(get_db)) -> Unidad:
    # selectinload trae el edificio en la misma consulta: evita el problema
    # N+1 (una query por cada relacion que se toca despues).
    stmt = (
        select(Unidad)
        .options(selectinload(Unidad.edificio))
        .where(Unidad.id == unidad_id)
    )
    unidad = db.scalar(stmt)
    if unidad is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No existe la unidad {unidad_id}")
    return unidad
