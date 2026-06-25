"""Punto de entrada del microservicio 2FA.

Composition root: crea la app FastAPI, registra los routers de cada feature y
crea las tablas de la base de datos al arrancar.

Ejecutar:
    uvicorn main:app --reload --port 8001
"""
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.database import init_db
from src.feature.oauth.infraestructure.routers.oauth_router import (
    router as oauth_router,
)
from src.feature.two_factor.infraestructure.routers.two_factor_router import (
    router as two_factor_router,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Microservicio 2FA",
    description="Genera, envía (Gmail) y valida códigos de doble factor.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS solo aplica a navegadores. Para tu flujo (app móvil -> API principal ->
# microservicio) queda cerrado por defecto. Configúralo con ALLOWED_ORIGINS solo
# si un frontend web necesita llamarlo directamente.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

app.include_router(two_factor_router)
app.include_router(oauth_router)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
    )
