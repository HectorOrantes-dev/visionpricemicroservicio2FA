"""Adaptador SMTP de Gmail con autenticación XOAUTH2.

smtplib es síncrono y bloqueante, así que la operación de red se ejecuta en un
hilo aparte (asyncio.to_thread) para no bloquear el event loop de FastAPI.
"""
import asyncio
import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from src.core.config import Settings
from src.feature.two_factor.domain.repositories.email_sender import EmailSender
from src.feature.two_factor.domain.repositories.token_provider import (
    AccessTokenProvider,
)

# Plantilla HTML del correo (src/feature/html/correo.html)
_TEMPLATE_PATH = (
    Path(__file__).resolve().parents[3] / "html" / "correo.html"
)


class SmtpEmailSender(EmailSender):
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

    def _build_message(self, to_email: str, code: str) -> MIMEMultipart:
        message = MIMEMultipart("alternative")
        message["Subject"] = "Tu código de verificación"
        message["From"] = (
            f"{self._settings.gmail_from_name} <{self._settings.gmail_from}>"
        )
        message["To"] = to_email
        text = f"Tu código de verificación es: {code}"
        message.attach(MIMEText(text, "plain"))
        message.attach(MIMEText(self._render_html(code), "html"))
        return message

    def _send_sync(self, to_email: str, code: str, access_token: str) -> None:
        message = self._build_message(to_email, code)
        auth_string = (
            f"user={self._settings.gmail_from}\x01"
            f"auth=Bearer {access_token}\x01\x01"
        )
        xoauth2 = base64.b64encode(auth_string.encode()).decode()

        with smtplib.SMTP(self._settings.smtp_host, self._settings.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            status, response = server.docmd("AUTH", "XOAUTH2 " + xoauth2)
            if status != 235:
                raise smtplib.SMTPAuthenticationError(status, response)
            server.send_message(message)

    async def send_code(self, to_email: str, code: str) -> None:
        access_token = await self._token_provider.get_access_token()
        await asyncio.to_thread(self._send_sync, to_email, code, access_token)
