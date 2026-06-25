"""Configuración de la base de datos (SQLAlchemy async).

Expone el engine, la fábrica de sesiones, la Base declarativa y un helper
para crear las tablas al arrancar la aplicación.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings

engine = create_async_engine(settings.async_database_url, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base declarativa para los modelos ORM."""


async def init_db() -> None:
    """Crea las tablas que aún no existan."""
    # Importa los modelos para que queden registrados en Base.metadata.
    from src.feature.oauth.infraestructure.adapters import sql_code_repository  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependencia de FastAPI: entrega una sesión y la cierra al final."""
    async with AsyncSessionLocal() as session:
        yield session
