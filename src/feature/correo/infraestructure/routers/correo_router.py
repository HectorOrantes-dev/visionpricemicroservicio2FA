"""Rutas HTTP de la feature correo (envío de correo genérico, texto libre).

Hoy lo usa Pagos/API principal para mandar el código de invitación a un
proyecto (ver CorreoAdapter2FA en visionpricebackend/src/features/proyectos).
Protegido igual que el resto del servicio: GatewayKeyMiddleware
(X-Gateway-Key, ver src/core/gateway_key.py — dual-accept mientras no sea
obligatorio).
"""
from fastapi import APIRouter, Depends, status

from src.feature.correo.infraestructure.controllers.correo_controller import (
    CorreoController,
    EnviarCorreoRequest,
    EnviarCorreoResponse,
)
from src.feature.correo.infraestructure.dependencies.dependencies import (
    get_correo_controller,
)

router = APIRouter(prefix="/correo", tags=["correo"])


@router.post(
    "/enviar",
    response_model=EnviarCorreoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def enviar_correo(
    payload: EnviarCorreoRequest,
    controller: CorreoController = Depends(get_correo_controller),
) -> EnviarCorreoResponse:
    return await controller.enviar(payload)
