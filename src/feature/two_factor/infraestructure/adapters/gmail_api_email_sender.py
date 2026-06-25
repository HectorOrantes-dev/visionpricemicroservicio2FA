"""Adaptador de envío vía API REST de Gmail (users.messages.send).

Funciona con el scope `gmail.send` (el que tiene el refresh_token actual), a
diferencia de SMTP que exige el scope amplio `https://mail.google.com/`.
"""
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import httpx

from src.core.config import Settings
from src.feature.two_factor.domain.repositories.email_sender import EmailSender
from src.feature.two_factor.domain.repositories.token_provider import (
    AccessTokenProvider,
)

_GMAIL_SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"

# Plantilla HTML del correo (src/feature/html/correo.html)
_TEMPLATE_PATH = Path(__file__).resolve().parents[3] / "html" / "correo.html"


class GmailApiEmailSender(EmailSender):
    def __init__(
        self,
        settings: Settings,
        token_provider: AccessTokenProvider,
    ) -> None:
        self._settings = settings
        self._token_provider = token_provider

    def _render_html(self, code: str) -> str:
        try:
            template = _TEMPLATE_PATH.read_text(encoding="utf-8")
        except FileNotFoundError:
            template = "<p>Tu código de verificación es: <b>{{code}}</b></p>"
        return template.replace("{{code}}", code)

    def _build_raw(self, to_email: str, code: str) -> str:
        message = MIMEMultipart("alternative")
        message["Subject"] = "Tu código de verificación"
        message["From"] = (
            f"{self._settings.gmail_from_name} <{self._settings.gmail_from}>"
        )
        message["To"] = to_email
        message.attach(MIMEText(f"Tu código de verificación es: {code}", "plain"))
        message.attach(MIMEText(self._render_html(code), "html"))
        return base64.urlsafe_b64encode(message.as_bytes()).decode()

    async def send_code(self, to_email: str, code: str) -> None:
        access_token = await self._token_provider.get_access_token()
        raw = self._build_raw(to_email, code)
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                _GMAIL_SEND_URL,
                headers={"Authorization": f"Bearer {access_token}"},
                json={"raw": raw},
            )
        response.raise_for_status()
