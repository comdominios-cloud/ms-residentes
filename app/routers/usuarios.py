"""Administracion de cuentas. Todo el router exige token."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Residente, Usuario
from app.schemas import UsuarioCreate, UsuarioOut
from app.security import hash_password, solo_admin, usuario_actual

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("", response_model=list[UsuarioOut])
def listar(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _: Usuario = Depends(usuario_actual),
) -> list[Usuario]:
    stmt = select(Usuario).order_by(Usuario.id).limit(limit).offset(offset)
    return list(db.scalars(stmt))


@router.post("", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear(
    datos: UsuarioCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(solo_admin),
) -> Usuario:
    if db.scalar(select(Usuario).where(Usuario.email == datos.email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe una cuenta con ese email")

    if datos.residente_id is not None and db.get(Residente, datos.residente_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No existe el residente {datos.residente_id}")

    usuario = Usuario(
        email=datos.email,
        password_hash=hash_password(datos.password),
        residente_id=datos.residente_id,
        rol=datos.rol,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    usuario_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(solo_admin),
) -> None:
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No existe el usuario {usuario_id}")

    if usuario.id == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No podes eliminar tu propia cuenta")

    db.delete(usuario)
    db.commit()
