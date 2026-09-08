"""Verificacion de tokens emitidos por ms-usuarios.

Este microservicio NO tiene tabla de usuarios: las cuentas viven en
ms-usuarios. Aca solo se verifica la FIRMA del token con el JWT_SECRET
compartido y se confia en los datos que trae adentro.

No hay llamada HTTP a ms-usuarios: la verificacion es local. Si alguien
modificara el rol dentro del token, la firma dejaria de coincidir.
"""

from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.security.tokens import decodificar_token

esquema_bearer = HTTPBearer(auto_error=False)

CREDENCIALES_INVALIDAS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token invalido o vencido",
    headers={"WWW-Authenticate": "Bearer"},
)


@dataclass(frozen=True)
class UsuarioToken:
    """Los datos del usuario, tal como vienen firmados dentro del token."""

    id: int
    email: str
    rol: str


def usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(esquema_bearer),
) -> UsuarioToken:
    if credenciales is None:
        raise CREDENCIALES_INVALIDAS

    datos = decodificar_token(credenciales.credentials)
    if datos is None or "sub" not in datos:
        raise CREDENCIALES_INVALIDAS

    return UsuarioToken(
        id=int(datos["sub"]),
        email=datos.get("email", ""),
        rol=datos.get("rol", "RESIDENTE"),
    )


def solo_admin(usuario: UsuarioToken = Depends(usuario_actual)) -> UsuarioToken:
    if usuario.rol != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requiere rol ADMIN",
        )
    return usuario
