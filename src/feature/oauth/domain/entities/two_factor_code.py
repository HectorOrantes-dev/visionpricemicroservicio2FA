"""Entidad de dominio: el código 2FA asociado a un usuario.

Representa la relación código <-> usuario y las reglas que determinan si un
código sigue siendo válido. No depende de FastAPI ni de SQLAlchemy.
"""
from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class TwoFactorCode:
    email: str
    code: str
    expires_at: datetime
    used: bool = False
    created_at: datetime = field(default_factory=_now)
    id: int | None = None

    @classmethod
    def generate(cls, email: str, *, length: int, ttl_seconds: int) -> "TwoFactorCode":
        """Crea un nuevo código numérico aleatorio para un usuario."""
        digits = "".join(secrets.choice("0123456789") for _ in range(length))
        return cls(
            email=email,
            code=digits,
            expires_at=_now() + timedelta(seconds=ttl_seconds),
        )

    def is_expired(self) -> bool:
        expires = self.expires_at
        if expires.tzinfo is None:  # por si la BD lo devuelve naive
            expires = expires.replace(tzinfo=timezone.utc)
        return _now() > expires

    def matches(self, candidate: str) -> bool:
        """¿El código propuesto es válido (correcto, no usado, no expirado)?"""
        return (
            not self.used
            and not self.is_expired()
            and secrets.compare_digest(self.code, candidate)
        )
