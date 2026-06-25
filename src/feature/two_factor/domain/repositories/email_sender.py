"""Puerto de salida: enviar el código por correo.

El dominio no sabe si por detrás hay Gmail, SES o un mock de tests.
"""
from abc import ABC, abstractmethod


class EmailSender(ABC):
    @abstractmethod
    async def send_code(self, to_email: str, code: str) -> None:
        """Envía el código 2FA al correo del usuario."""
