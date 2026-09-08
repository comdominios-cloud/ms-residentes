"""Dependencias de autenticacion para los endpoints protegidos.

Se usan asi:

    @router.get("/algo")
    def handler(usuario: Usuario = Depends(usuario_actual)):
        ...

FastAPI resuelve la dependencia antes de entrar al handler: si el token falta,
vencio o es invalido, corta con 401 y el handler nunca se ejecuta.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Usuario
from app.security.tokens import decodificar_token

# auto_error=False para poder devolver nuestro propio mensaje de error.
esquema_bearer = HTTPBearer(auto_error=False)

CREDENCIALES_INVALIDAS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token invalido o vencido",
    headers={"WWW-Authenticate": "Bearer"},
)


def usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(esquema_bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    if credenciales is None:
        raise CREDENCIALES_INVALIDAS

    datos = decodificar_token(credenciales.credentials)
    if datos is None or "sub" not in datos:
        raise CREDENCIALES_INVALIDAS

    usuario = db.get(Usuario, int(datos["sub"]))
    if usuario is None or not usuario.activo:
        raise CREDENCIALES_INVALIDAS

    return usuario


def solo_admin(usuario: Usuario = Depends(usuario_actual)) -> Usuario:
    """Igual que `usuario_actual` pero ademas exige rol ADMIN."""
    if usuario.rol != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requiere rol ADMIN",
        )
    return usuario
