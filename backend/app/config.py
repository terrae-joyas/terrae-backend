"""
Configuración central del backend Terrae.

Lee las variables de entorno definidas en `.env` (ver `.env.example` en la
raíz del repositorio). Este módulo es la única fuente de configuración:
ningún otro archivo debe leer `os.environ` directamente.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Entorno ---
    environment: str = "development"
    debug: bool = True

    # --- API ---
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_version: str = "v1"
    api_secret_key: str = "changeme"
    cors_origins: str = "http://localhost:3000"

    # --- Base de datos (usada a partir de la Etapa 5) ---
    database_url: str | None = None

    # --- Autenticación / JWT (Etapa 4) ---
    jwt_secret_key: str = "changeme"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7
    usuarios_data_path: str = "app/infrastructure/data/usuarios.json"

    # --- Blockchain (usada a partir de la Etapa 12) ---
    blockchain_gateway_mode: str = "simulado"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Devuelve una instancia cacheada de Settings (evita releer .env en cada request)."""
    return Settings()
