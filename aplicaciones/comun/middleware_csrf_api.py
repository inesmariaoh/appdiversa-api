"""
Middleware que exime rutas JSON de la API del control CSRF de formularios HTML.
"""


class EximirCsrfRutasApiMiddleware:
    """Desactiva CSRF en /api/v1/ para clientes SPA con CORS y credenciales."""

    PREFIJO_RUTAS_API = "/api/v1/"

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(self.PREFIJO_RUTAS_API):
            request._dont_enforce_csrf_checks = True
        return self.get_response(request)
