"""Inyección de dependencias de la feature two_factor (composition root local).

Aquí se ensambla la cadena hexagonal: repositorio SQL (de oauth) + proveedor de
token de Google + SMTP, todo inyectado en el caso de uso de envío.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_session
from src.feature.oauth.application.register_code_use_case import RegisterCodeUseCase
from src.feature.oauth.infraestructure.adapters.sql_code_repository import (
    SqlCodeRepository,
)
from src.feature.two_factor.application.send_code_use_case import (
    SendTwoFactorCodeUseCase,
)
from src.feature.two_factor.domain.repositories.email_sender import EmailSender
from src.feature.two_factor.infraestructure.adapters.gmail_token_provider import (
    GmailAccessTokenProvider,
)
from src.feature.two_factor.infraestructure.adapters.gmail_api_email_sender import (
    GmailApiEmailSender,
)
from src.feature.two_factor.infraestructure.controllers.two_factor_controller import (
    TwoFactorController,
)

# El proveedor de token se cachea a nivel de proceso (reutiliza el access token).
_token_provider = GmailAccessTokenProvider(settings)


def get_email_sender() -> EmailSender:
    return GmailApiEmailSender(settings, _token_provider)


def get_two_factor_controller(
    session: AsyncSession = Depends(get_session),
    email_sender: EmailSender = Depends(get_email_sender),
) -> TwoFactorController:
    register_code = RegisterCodeUseCase(SqlCodeRepository(session))
    send_use_case = SendTwoFactorCodeUseCase(
        register_code,
        email_sender,
        code_length=settings.code_length,
        code_ttl_seconds=settings.code_ttl_seconds,
    )
    return TwoFactorController(send_use_case)
