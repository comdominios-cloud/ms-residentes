"""Registro e inicio de sesion."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import get_db
from app.models import Residente, Usuario
from app.schemas import LoginRequest, RegisterRequest, TokenResponse, UsuarioOut
from app.security import crear_access_token, hash_password, usuario_actual, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(datos: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Crea una cuenta y devuelve el token, para no obligar a un login extra."""
    ya_existe = db.scalar(select(Usuario).where(Usuario.email == datos.email))
    if ya_existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta con ese email",
        )

    if datos.residente_id is not None and db.get(Residente, datos.residente_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe el residente {datos.residente_id}",
        )

    usuario = Usuario(
        email=datos.email,
        password_hash=hash_password(datos.password),
        residente_id=datos.residente_id,
        rol="RESIDENTE",
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return _token_para(usuario)


@router.post("/login", response_model=TokenResponse)
def login(datos: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    usuario = db.scalar(select(Usuario).where(Usuario.email == datos.email))

    # Mismo mensaje si el email no existe o si la password esta mal: no le
    # confirmamos a un atacante que ese email esta registrado.
    if usuario is None or not verify_password(datos.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o password incorrectos",
        )

    if not usuario.activo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cuenta desactivada")

    usuario.ultimo_login = datetime.now(UTC).replace(tzinfo=None)
    db.commit()
    db.refresh(usuario)

    return _token_para(usuario)


@router.get("/me", response_model=UsuarioOut)
def me(usuario: Usuario = Depends(usuario_actual)) -> Usuario:
    """Devuelve la cuenta duena del token. Sirve para validar la sesion."""
    return usuario


def _token_para(usuario: Usuario) -> TokenResponse:
    return TokenResponse(
        access_token=crear_access_token(usuario.id, usuario.email, usuario.rol),
        expires_in=settings.jwt_expire_minutes * 60,
        usuario=UsuarioOut.model_validate(usuario),
    )
