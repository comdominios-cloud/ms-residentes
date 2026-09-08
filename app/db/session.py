"""Conexion a PostgreSQL.

- `engine`: pool de conexiones, se crea una vez al arrancar la app.
- `SessionLocal`: fabrica de sesiones (una sesion = una conversacion con la BD).
- `get_db()`: dependencia de FastAPI. Entrega una sesion al endpoint y la
  cierra cuando el request termina, haya salido bien o mal.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    # Verifica que la conexion siga viva antes de usarla. Evita el error
    # "server closed the connection" cuando la BD estuvo un rato inactiva.
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
