"""Adaptador: intercambia el refresh_token de Google por un access_token.

Cachea el token en memoria hasta poco antes de que expire para no pedir uno
nuevo en cada envío.
"""
import time

import httpx

from src.core.config import Settings
from src.feature.two_factor.domain.repositories.token_provider import (
    AccessTokenProvider,
)


class GmailAccessTokenProvider(AccessTokenProvider):
    # margen de seguridad antes de la expiración real (segundos)
    _EXPIRY_MARGIN = 60

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._cached_token: str | None = None
        self._expires_at: float = 0.0

    async def get_access_token(self) -> str:
        if self._cached_token and time.time() < self._expires_at:
            return self._cached_token

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                self._settings.google_token_uri,
                data={
                    "client_id": self._settings.gmail_client_id,
                    "client_secret": self._settings.gmail_client_secret,
                    "refresh_token": self._settings.gmail_refresh_token,
                    "grant_type": "refresh_token",
                },
            )
        response.raise_for_status()
        payload = response.json()

        token = payload["access_token"]
        expires_in = int(payload.get("expires_in", 3600))
        self._cached_token = token
        self._expires_at = time.time() + expires_in - self._EXPIRY_MARGIN
        return token
