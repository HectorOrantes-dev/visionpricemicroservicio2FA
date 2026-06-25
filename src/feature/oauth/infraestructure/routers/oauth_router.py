"""Rutas HTTP de la feature oauth (validación del código 2FA)."""
from fastapi import APIRouter, Depends

from src.feature.oauth.infraestructure.controllers.oauth_controller import (
    OAuthController,
    VerifyRequest,
    VerifyResponse,
)
from src.feature.oauth.infraestructure.dependencies.dependencies import (
    get_oauth_controller,
)

router = APIRouter(prefix="/2fa", tags=["2FA - Validación"])


@router.post("/verify", response_model=VerifyResponse)
async def verify_code(
    payload: VerifyRequest,
    controller: OAuthController = Depends(get_oauth_controller),
) -> VerifyResponse:
    """Valida el código que el usuario introdujo. La API principal confía en `valid`."""
    return await controller.verify(payload)
