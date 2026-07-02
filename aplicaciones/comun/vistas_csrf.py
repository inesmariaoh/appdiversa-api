"""
Vista de respuesta ante fallos de validacion CSRF.
"""

from django.http import HttpRequest, JsonResponse

from aplicaciones.comun.constantes_seguridad import MensajesErrorApi


def respuesta_csrf_fallida(
    _solicitud: HttpRequest,
    reason: str = "",
) -> JsonResponse:
    """Retorna un mensaje funcional cuando falla la validacion CSRF."""
    _ = reason
    return JsonResponse(
        {"detalle": MensajesErrorApi.SOLICITUD_NO_VALIDA},
        status=403,
    )
