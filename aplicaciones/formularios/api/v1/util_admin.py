"""
Utilidades compartidas para vistas administrativas de formularios.
"""

from collections.abc import Callable
from typing import TypeVar

from rest_framework import status
from rest_framework.response import Response

from aplicaciones.formularios.excepciones_admin import ValidacionFormularioAdminError

T = TypeVar("T")

_ERRORES_NO_ENCONTRADO: tuple[type[Exception], ...] = ()


def registrar_errores_no_encontrado(*clases: type[Exception]) -> None:
    """Registra clases de excepcion que mapean a HTTP 404."""
    global _ERRORES_NO_ENCONTRADO  # noqa: PLW0603
    _ERRORES_NO_ENCONTRADO = (*_ERRORES_NO_ENCONTRADO, *clases)


def ejecutar_servicio_admin(
    operacion: Callable[[], T],
    errores_no_encontrado: tuple[type[Exception], ...],
) -> tuple[T | None, Response | None]:
    """Ejecuta un servicio y traduce excepciones funcionales a respuestas HTTP."""
    try:
        return operacion(), None
    except ValidacionFormularioAdminError as error:
        return None, Response({"detalle": error.mensaje}, status=status.HTTP_400_BAD_REQUEST)
    except errores_no_encontrado as error:
        mensaje = getattr(error, "mensaje", str(error))
        return None, Response({"detalle": mensaje}, status=status.HTTP_404_NOT_FOUND)
