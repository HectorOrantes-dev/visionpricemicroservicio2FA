"""Caso de uso: registrar (relacionar) un código con un usuario.

Lo invoca la feature `two_factor` justo después de generar el código, para
que quede persistido y luego se pueda validar.
"""
from src.feature.oauth.domain.entities.two_factor_code import TwoFactorCode
from src.feature.oauth.domain.repositories.code_repository import CodeRepository


class RegisterCodeUseCase:
    def __init__(self, repository: CodeRepository) -> None:
        self._repository = repository

    async def execute(self, code: TwoFactorCode) -> TwoFactorCode:
        # Un solo código activo por usuario: invalida los anteriores.
        await self._repository.invalidate_previous(code.email)
        return await self._repository.save(code)
