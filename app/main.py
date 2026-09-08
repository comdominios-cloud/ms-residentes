"""Punto de entrada de ms-residentes.

Microservicio de edificios, unidades, residentes y usuarios del condominio.
"""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import get_db
from app.routers import auth, edificios, residentes, unidades, usuarios

settings = get_settings()

app = FastAPI(
    title="ms-residentes",
    description=(
        "Microservicio de edificios, unidades y residentes del condominio. "
        "Incluye la gestion de usuarios: register, login, alta y baja."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS: sin esto el navegador bloquea las llamadas del frontend (Amplify) hacia
# esta API, aunque desde Postman funcionen perfecto.
# TODO: en produccion reemplazar "*" por el dominio real de Amplify.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(edificios.router)
app.include_router(unidades.router)
app.include_router(residentes.router)


@app.get("/health", tags=["health"])
def health(db: Session = Depends(get_db)) -> dict:
    """Health check real: comprueba que la base responda, no solo que la app viva."""
    try:
        db.execute(text("SELECT 1"))
        base = "ok"
    except Exception:
        base = "error"

    return {
        "status": "ok" if base == "ok" else "degraded",
        "service": settings.app_name,
        "database": base,
    }
