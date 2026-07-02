"""
Autenticacion por sesion Django para consumo desde SPA con CORS.
"""

from rest_framework.authentication import SessionAuthentication


class AutenticacionSesionApi(SessionAuthentication):
    """Valida sesion Django sin exigir token CSRF en cabecera."""

    def enforce_csrf(self, request) -> None:
        """Omite CSRF en la API; el control de origen se realiza con CORS."""
