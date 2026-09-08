"""Residentes del condominio.

Lectura publica; escritura con token.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models import Residente, Unidad
from app.schemas import ResidenteCreate, ResidenteDetalle, ResidenteOut, ResidenteUpdate
from app.security import UsuarioToken, usuario_actual

router = APIRouter(prefix="/residentes", tags=["residentes"])


@router.get("", response_model=list[ResidenteOut])
def listar(
    unidad_id: int | None = Query(None, description="Filtra por unidad"),
    activo: bool | None = Query(None, description="Filtra por estado"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[Residente]:
    stmt = select(Residente).order_by(Residente.id).limit(limit).offset(offset)
    if unidad_id is not None:
        stmt = stmt.where(Residente.unidad_id == unidad_id)
    if activo is not None:
        stmt = stmt.where(Residente.activo == activo)
    return list(db.scalars(stmt))


@router.get("/{residente_id}", response_model=ResidenteDetalle)
def obtener(residente_id: int, db: Session = Depends(get_db)) -> Residente:
    stmt = (
        select(Residente)
        .options(selectinload(Residente.unidad))
        .where(Residente.id == residente_id)
    )
    residente = db.scalar(stmt)
    if residente is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No existe el residente {residente_id}")
    return residente


@router.post("", response_model=ResidenteOut, status_code=status.HTTP_201_CREATED)
def crear(
    datos: ResidenteCreate,
    db: Session = Depends(get_db),
    _: UsuarioToken = Depends(usuario_actual),
) -> Residente:
    if db.get(Unidad, datos.unidad_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No existe la unidad {datos.unidad_id}")

    if db.scalar(select(Residente).where(Residente.documento == datos.documento)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un residente con ese documento")

    residente = Residente(**datos.model_dump())
    db.add(residente)
    db.commit()
    db.refresh(residente)
    return residente


@router.put("/{residente_id}", response_model=ResidenteOut)
def actualizar(
    residente_id: int,
    datos: ResidenteUpdate,
    db: Session = Depends(get_db),
    _: UsuarioToken = Depends(usuario_actual),
) -> Residente:
    residente = db.get(Residente, residente_id)
    if residente is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No existe el residente {residente_id}")

    # exclude_unset: solo toca los campos que vinieron en el body.
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(residente, campo, valor)

    db.commit()
    db.refresh(residente)
    return residente


@router.delete("/{residente_id}", status_code=status.HTTP_204_NO_CONTENT)
def dar_de_baja(
    residente_id: int,
    db: Session = Depends(get_db),
    _: UsuarioToken = Depends(usuario_actual),
) -> None:
    """Soft delete: marca `activo = false` en vez de borrar la fila.

    Borrarla romperia la clave foranea de `usuarios` y se perderia el historial.
    """
    residente = db.get(Residente, residente_id)
    if residente is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No existe el residente {residente_id}")

    residente.activo = False
    db.commit()
