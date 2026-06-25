"""Caso de uso: validar el código 2FA que envía la API principal."""
from dataclasses import dataclass

from src.feature.oauth.domain.repositories.code_repository import CodeRepository


@dataclass
class VerificationResult:
    valid: bool
    reason: str


class VerifyCodeUseCase:
    def __init__(self, repository: CodeRepository) -> None:
        self._repository = repository

    async def execute(self, email: str, candidate: str) -> VerificationResult:
        stored = await self._repository.find_active_by_email(email)

        if stored is None:
            return VerificationResult(False, "no_active_code")

        if stored.is_expired():
            return VerificationResult(False, "expired")

        if not stored.matches(candidate):
            return VerificationResult(False, "invalid_code")

        # Código correcto: se consume para que no pueda reutilizarse.
        await self._repository.mark_used(stored.id)
        return VerificationResult(True, "ok")
