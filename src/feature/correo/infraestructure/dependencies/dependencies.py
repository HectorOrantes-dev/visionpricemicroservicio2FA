"""Inyección de dependencias de la feature correo (correo genérico)."""
from fastapi import Depends

from src.core.config import settings
from src.feature.correo.domain.repositories.generic_email_sender import (
    GenericEmailSender,
)
from src.feature.correo.infraestructure.adapters.gmail_generic_email_sender import (
    GmailGenericEmailSender,
)
from src.feature.correo.infraestructure.controllers.correo_controller import (
    CorreoController,
)
from src.feature.two_factor.infraestructure.adapters.gmail_token_provider import (
    GmailAccessTokenProvider,
)

# Instancia propia de esta feature (cachea su propio access_token en
# memoria, igual que la de two_factor) — mismas credenciales del .env,
# sin acoplarse a la instancia interna de two_factor.
_token_provider = GmailAccessTokenProvider(settings)


def get_generic_email_sender() -> GenericEmailSender:
    return GmailGenericEmailSender(settings, _token_provider)


def get_correo_controller(
    sender: GenericEmailSender = Depends(get_generic_email_sender),
) -> CorreoController:
    return CorreoController(sender)
