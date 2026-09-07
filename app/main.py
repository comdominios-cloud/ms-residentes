"""Punto de entrada de ms-residentes.

ANDAMIAJE: solo instancia la aplicacion FastAPI y expone Swagger-UI.
Los endpoints, modelos y logica de negocio se implementan mas adelante.

Dominio: edificios, unidades, residentes y los usuarios del sistema
(registro, login y administracion de cuentas).
"""

from fastapi import FastAPI

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


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": "ms-residentes"}


# TODO: app.include_router(...) por cada router de app/routers/
# TODO: hashing de passwords y emision de JWT en app/security/
