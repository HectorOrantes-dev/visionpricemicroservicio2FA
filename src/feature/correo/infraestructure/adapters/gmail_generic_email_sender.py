"""Adaptador de correo genérico vía la API REST de Gmail.

Mismo mecanismo que `GmailApiEmailSender` (two_factor): la misma app de
Gmail ya autorizada con scope `gmail.send` y el mismo refresh_token del
`.env`. La diferencia es que no hay una plantilla fija de "código de
verificación" — el asunto y el cuerpo los define quien llama al endpoint.
"""
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx

from src.core.config import Settings
from src.feature.correo.domain.repositories.generic_email_sender import (
    GenericEmailSender,
)
from src.feature.two_factor.domain.repositories.token_provider import (
    AccessTokenProvider,
)

_GMAIL_SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"


class GmailGenericEmailSender(GenericEmailSender):
    def __init__(
        self,
        settings: Settings,
        token_provider: AccessTokenProvider,
    ) -> None:
        self._settings = settings
        self._token_provider = token_provider

    def _build_raw(self, to_email: str, subject: str, body_text: str) -> str:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = (
            f"{self._settings.gmail_from_name} <{self._settings.gmail_from}>"
        )
        message["To"] = to_email
        message.attach(MIMEText(body_text, "plain"))
        html = "<p>" + body_text.replace("\n", "<br>") + "</p>"
        message.attach(MIMEText(html, "html"))
        return base64.urlsafe_b64encode(message.as_bytes()).decode()

    async def send(self, to_email: str, subject: str, body_text: str) -> None:
        access_token = await self._token_provider.get_access_token()
        raw = self._build_raw(to_email, subject, body_text)
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                _GMAIL_SEND_URL,
                headers={"Authorization": f"Bearer {access_token}"},
                json={"raw": raw},
            )
        response.raise_for_status()
