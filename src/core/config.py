"""Configuración central del microservicio.

Carga las variables del archivo .env usando pydantic-settings y las expone
como un único objeto `settings` que se inyecta donde haga falta.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Credenciales Google OAuth2 (para enviar correo vía Gmail) ---
    gmail_client_id: str
    gmail_client_secret: str
    gmail_refresh_token: str
    gmail_from: str
    gmail_from_name: str = "2FA"
    google_token_uri: str = "https://oauth2.googleapis.com/token"

    # --- SMTP ---
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587

    # --- Base de datos ---
    database_url: str = "sqlite+aiosqlite:///./2fa.db"

    # --- Código 2FA ---
    code_length: int = 6
    code_ttl_seconds: int = 300

    # --- Servidor ---
    app_host: str = "0.0.0.0"
    app_port: int = 8001

    # --- CORS ---
    # Orígenes de NAVEGADOR permitidos, separados por coma. Vacío = ninguno,
    # que es lo correcto para un servicio que solo llama tu backend.
    # Ej. para un frontend web: "https://app.visionprice.com,https://admin.visionprice.com"
    allowed_origins: str = ""

    # --- API Gateway (tráfico entrante vía el gateway) ---
    # Fase OPCIONAL: si está vacío, no-op. Si está seteado, valida
    # X-Gateway-Key CUANDO viene pero no lo exige todavía (dual-accept
    # mientras el backend principal migra a llamar acá vía el gateway).
    # IMPORTANTE: hoy este servicio no tiene NINGUNA autenticación en
    # /2fa/send ni /2fa/verify — configurar esto es el primer paso real
    # para cerrar ese hueco.
    gateway_shared_key: str = ""

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def async_database_url(self) -> str:
        """Normaliza la URL para el driver async.

        Railway (y otros) entregan `postgresql://...`; SQLAlchemy async necesita
        `postgresql+asyncpg://...`. Convertimos el esquema si hace falta.
        """
        url = self.database_url
        if url.startswith("postgresql+"):
            return url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    """Devuelve una única instancia de Settings (cacheada)."""
    return Settings()


settings = get_settings()
