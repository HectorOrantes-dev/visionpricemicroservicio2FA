"""Puerto de salida: enviar un correo de texto libre (asunto + cuerpo).

Distinto de `EmailSender` (two_factor): ese envía siempre el mismo template
de "código de verificación". Este lo usan otros microservicios (ej. Pagos/
API principal) para mandar avisos con contenido propio — hoy, el código de
invitación a un proyecto.
"""
from abc import ABC, abstractmethod


class GenericEmailSender(ABC):
    @abstractmethod
    async def send(self, to_email: str, subject: str, body_text: str) -> None:
        """Envía un correo de texto libre al destinatario."""
