"""Validacion de los JSON Web Tokens que emite ms-usuarios.

Este servicio no emite tokens, solo los verifica: el JWT_SECRET tiene que ser
el mismo que usa ms-usuarios para firmarlos.
"""

from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()


def decodificar_token(token: str) -> dict | None:
    """Devuelve el contenido del token, o None si esta vencido o adulterado."""
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
