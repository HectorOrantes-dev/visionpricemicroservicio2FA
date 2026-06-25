"""Rutas HTTP de la feature two_factor (envío del código 2FA)."""
from fastapi import APIRouter, Depends, status

from src.feature.two_factor.infraestructure.controllers.two_factor_controller import (
    SendRequest,
    SendResponse,
    TwoFactorController,
)
from src.feature.two_factor.infraestructure.dependencies.dependencies import (
    get_two_factor_controller,
)

router = APIRouter(prefix="/2fa", tags=["2FA - Envío"])


@router.post("/send", response_model=SendResponse, status_code=status.HTTP_201_CREATED)
async def send_code(
    payload: SendRequest,
    controller: TwoFactorController = Depends(get_two_factor_controller),
) -> SendResponse:
    """La API principal llama aquí tras el login para enviar el código al correo."""
    return await controller.send(payload)
