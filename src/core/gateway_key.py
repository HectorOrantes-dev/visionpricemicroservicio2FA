"""Middleware de validación del API Gateway (fase de rollout OPCIONAL).

Este servicio hoy NO TIENE ninguna autenticación en /2fa/send ni /2fa/verify
— cualquiera que sepa la URL puede disparar códigos para cualquier
teléfono/correo. Este middleware es el primer paso para cerrar eso.

Montaje (en main.py):
    from src.core.gateway_key import GatewayKeyMiddleware
    app.add_middleware(GatewayKeyMiddleware)

Comportamiento actual (dual-accept, para no romper el backend principal
mientras migra a llamar acá vía el gateway en vez de directo):
  - settings.gateway_shared_key vacío       -> no-op total (como hoy).
  - Header X-Gateway-Key AUSENTE            -> deja pasar igual (rollout).
  - Header X-Gateway-Key PRESENTE pero mal  -> 401, corta acá.
  - Header X-Gateway-Key PRESENTE y OK      -> pasa.

Cuando el rollout esté completo, cambiar la rama "ausente" para que también
rechace — ese es el modo estricto (un cambio de una línea acá).
"""
import hmac
import json

from src.core.config import settings

_EXCLUIDOS = ("/health",)


class GatewayKeyMiddleware:
    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not settings.gateway_shared_key:
            return await self.app(scope, receive, send)

        path = scope.get("path", "")
        if path in _EXCLUIDOS:
            return await self.app(scope, receive, send)

        recibida = _header(scope, b"x-gateway-key")
        if recibida is not None and not hmac.compare_digest(
            recibida.decode(), settings.gateway_shared_key
        ):
            return await _rechazar(send)

        return await self.app(scope, receive, send)


def _header(scope, nombre: bytes) -> bytes | None:
    for k, v in scope["headers"]:
        if k == nombre:
            return v
    return None


async def _rechazar(send) -> None:
    body = json.dumps({"detail": "X-Gateway-Key inválida."}).encode()
    await send(
        {
            "type": "http.response.start",
            "status": 401,
            "headers": [(b"content-type", b"application/json")],
        }
    )
    await send({"type": "http.response.body", "body": body})
