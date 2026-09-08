"""Emision y validacion de JSON Web Tokens.

Un JWT tiene tres partes: cabecera.datos.firma
El servidor no guarda sesiones: valida la firma con JWT_SECRET y confia en los
datos que el token trae adentro.
"""

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()


def crear_access_token(usuario_id: int, email: str, rol: str) -> str:
    ahora = datetime.now(UTC)
    payload = {
        "sub": str(usuario_id),   # 'subject': de quien es el token
        "email": email,
        "rol": rol,
        "iat": ahora,                                                   # emitido
        "exp": ahora + timedelta(minutes=settings.jwt_expire_minutes),  # vence
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decodificar_token(token: str) -> dict | None:
    """Devuelve el contenido del token, o None si esta vencido o adulterado."""
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
