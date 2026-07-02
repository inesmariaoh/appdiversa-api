"""
Manejador de excepciones de la API con formato funcional en espanol.
"""

from rest_framework.exceptions import APIException, NotAuthenticated, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import exception_handler

from aplicaciones.comun.constantes_seguridad import MensajesAccesoApi, MensajesErrorApi
from aplicaciones.comun.utilidades_mensajes_error import normalizar_mensaje_error_cliente


def _respuesta_detalle(
    mensaje: str,
    codigo_estado: int,
    mensaje_por_defecto: str | None = None,
) -> Response:
    """Construye una respuesta JSON con campo detalle normalizado."""
    return Response(
        {
            "detalle": normalizar_mensaje_error_cliente(
                mensaje,
                mensaje_por_defecto,
            ),
        },
        status=codigo_estado,
    )


def manejador_excepciones_api(exc: Exception, context: dict) -> Response | None:
    """Normaliza respuestas de error al contrato JSON con campo detalle."""
    if isinstance(exc, NotAuthenticated):
        return _respuesta_detalle(str(exc.detail), 401)

    if isinstance(exc, PermissionDenied):
        return _respuesta_detalle(
            str(exc.detail),
            403,
            mensaje_por_defecto=MensajesAccesoApi.ACCESO_DENEGADO,
        )

    respuesta = exception_handler(exc, context)
    if respuesta is None:
        return None

    if isinstance(respuesta.data, dict):
        detalle = respuesta.data.get("detalle", respuesta.data.get("detail"))
        if detalle is not None:
            respuesta.data = {
                "detalle": normalizar_mensaje_error_cliente(detalle),
            }
            return respuesta

        if respuesta.data:
            respuesta.data = {
                "detalle": normalizar_mensaje_error_cliente(respuesta.data),
            }
            return respuesta

    if isinstance(exc, APIException):
        respuesta.data = {
            "detalle": normalizar_mensaje_error_cliente(exc.detail),
        }

    return respuesta
