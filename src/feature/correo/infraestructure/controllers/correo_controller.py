"""Controller de correo genérico: envía un correo de texto libre."""
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from src.feature.correo.domain.repositories.generic_email_sender import (
    GenericEmailSender,
)


class EnviarCorreoRequest(BaseModel):
    correo: EmailStr
    asunto: str = Field(..., min_length=1, max_length=200)
    cuerpo: str = Field(..., min_length=1, max_length=5000)


class EnviarCorreoResponse(BaseModel):
    correo: EmailStr
    sent: bool


class CorreoController:
    def __init__(self, sender: GenericEmailSender) -> None:
        self._sender = sender

    async def enviar(self, payload: EnviarCorreoRequest) -> EnviarCorreoResponse:
        try:
            await self._sender.send(payload.correo, payload.asunto, payload.cuerpo)
        except Exception as exc:  # fallo SMTP/API de Gmail o token de Google
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"No se pudo enviar el correo: {exc}",
            ) from exc
        return EnviarCorreoResponse(correo=payload.correo, sent=True)
