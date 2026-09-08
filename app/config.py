"""Configuracion de la aplicacion.

Lee las variables de entorno una sola vez al arrancar y las valida.
Si falta alguna obligatoria, la app no levanta y avisa cual.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Aplicacion
    app_name: str = "ms-residentes"
    app_env: str = "development"
    app_port: int = 8000
    log_level: str = "info"

    # PostgreSQL
    postgres_host: str
    postgres_port: int = 5432
    postgres_db: str
    postgres_user: str
    postgres_password: str

    # Autenticacion
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    @property
    def database_url(self) -> str:
        """Cadena de conexion que entiende SQLAlchemy + psycopg 3."""
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    """Cacheada: el .env se lee una vez, no en cada request."""
    return Settings()
