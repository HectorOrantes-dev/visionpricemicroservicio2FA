"""Puerto de salida: obtener un access token de Google.

Abstrae el intercambio del refresh_token por un access_token vigente, que es
lo que necesita SMTP de Gmail para autenticarse vía XOAUTH2.
"""
from abc import ABC, abstractmethod


class AccessTokenProvider(ABC):
    @abstractmethod
    async def get_access_token(self) -> str:
        """Devuelve un access token de Google válido."""
