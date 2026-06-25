"""Caso de uso: generar un código 2FA y enviarlo por correo.

Orquesta tres pasos:
  1. genera el código (entidad de dominio),
  2. lo registra/relaciona con el usuario (feature oauth),
  3. lo envía por correo (puerto EmailSender).
"""
from dataclasses import dataclass

from src.feature.oauth.application.register_code_use_case import RegisterCodeUseCase
from src.feature.oauth.domain.entities.two_factor_code import TwoFactorCode
from src.feature.two_factor.domain.repositories.email_sender import EmailSender


@dataclass
class SendCodeResult:
    email: str
    sent: bool
    expires_at: str


class SendTwoFactorCodeUseCase:
    def __init__(
        self,
        register_code: RegisterCodeUseCase,
        email_sender: EmailSender,
        *,
        code_length: int,
        code_ttl_seconds: int,
    ) -> None:
        self._register_code = register_code
        self._email_sender = email_sender
        self._code_length = code_length
        self._code_ttl_seconds = code_ttl_seconds

    async def execute(self, email: str) -> SendCodeResult:
        code = TwoFactorCode.generate(
            email,
            length=self._code_length,
            ttl_seconds=self._code_ttl_seconds,
        )
        await self._register_code.execute(code)
        await self._email_sender.send_code(email, code.code)
        return SendCodeResult(
            email=email,
            sent=True,
            expires_at=code.expires_at.isoformat(),
        )
