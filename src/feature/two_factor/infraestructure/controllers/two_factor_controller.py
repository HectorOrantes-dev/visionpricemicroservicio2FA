"""Controller de two_factor: orquesta la generación y envío del código."""
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr

from src.feature.two_factor.application.send_code_use_case import (
    SendTwoFactorCodeUseCase,
)


class SendRequest(BaseModel):
    email: EmailStr


class SendResponse(BaseModel):
    email: EmailStr
    sent: bool
    expires_at: str


class TwoFactorController:
    def __init__(self, send_use_case: SendTwoFactorCodeUseCase) -> None:
        self._send_use_case = send_use_case

    async def send(self, payload: SendRequest) -> SendResponse:
        try:
            result = await self._send_use_case.execute(payload.email)
        except Exception as exc:  # fallo SMTP / token de Google
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"No se pudo enviar el código: {exc}",
            ) from exc
        return SendResponse(
            email=result.email,
            sent=result.sent,
            expires_at=result.expires_at,
        )
