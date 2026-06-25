"""Puerto (interfaz) del repositorio de códigos 2FA.

El dominio define QUÉ se necesita; la infraestructura decide CÓMO (SQL, Redis...).
"""
from abc import ABC, abstractmethod

from src.feature.oauth.domain.entities.two_factor_code import TwoFactorCode


class CodeRepository(ABC):
    @abstractmethod
    async def save(self, code: TwoFactorCode) -> TwoFactorCode:
        """Persiste un código recién generado y devuelve la entidad con id."""

    @abstractmethod
    async def find_active_by_email(self, email: str) -> TwoFactorCode | None:
        """Devuelve el último código no usado y no expirado de un usuario."""

    @abstractmethod
    async def mark_used(self, code_id: int) -> None:
        """Marca un código como usado (consumido) para que no se reutilice."""

    @abstractmethod
    async def invalidate_previous(self, email: str) -> None:
        """Invalida códigos anteriores del usuario antes de emitir uno nuevo."""
