"""
Middleware para establecer el contexto de auditoria por solicitud.
"""

from typing import Callable

from django.http import HttpRequest, HttpResponse

from aplicaciones.auditoria.constantes import (
    HEADER_KEYCLOAK_USER_ID,
    HEADER_SESION_ANONIMA,
)
from aplicaciones.auditoria.contexto import (
    establecer_contexto_auditoria,
    limpiar_contexto_auditoria,
)


class AuditoriaContextoMiddleware:
    """Captura datos de auditoria desde la solicitud HTTP."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        usuario = request.user if request.user.is_authenticated else None
        identificador_keycloak = request.META.get(HEADER_KEYCLOAK_USER_ID, "")
        uuid_sesion_anonima = request.META.get(HEADER_SESION_ANONIMA, "")
        ip = self._obtener_ip_segura(request)
        user_agent = str(request.META.get("HTTP_USER_AGENT", ""))

        establecer_contexto_auditoria(
            usuario=usuario,
            identificador_keycloak=str(identificador_keycloak),
            uuid_sesion_anonima=str(uuid_sesion_anonima),
            ip=ip,
            user_agent=user_agent,
        )

        try:
            return self.get_response(request)
        finally:
            limpiar_contexto_auditoria()

    def _obtener_ip_segura(self, request: HttpRequest) -> str | None:
        """Extrae la IP del cliente de forma segura."""
        reenviado = request.META.get("HTTP_X_FORWARDED_FOR")
        if reenviado:
            return str(reenviado).split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
