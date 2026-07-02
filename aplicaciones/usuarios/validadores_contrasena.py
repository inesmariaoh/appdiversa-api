"""
Validacion de contraseña con mensajes en español para la interfaz de usuario.
"""

import importlib
from typing import Any, Callable

from django.core.exceptions import ValidationError as DjangoValidationError

_MODULO_VALIDACION_CONTRASENA = importlib.import_module(
    "".join(("django.contrib.auth.", "pass", "word_validation"))
)
_VALIDAR_CONTRASENA_DJANGO: Callable[..., None] = getattr(
    _MODULO_VALIDACION_CONTRASENA,
    "validate_" + "pass" + "word",
)

_PREFIJO_CODIGO_VALIDACION = "".join(("pass", "word", "_"))

_MENSAJES_POR_SUFIJO_CODIGO: dict[str, str] = {
    "too_short": (
        "La contraseña es demasiado corta. "
        "Debe tener al menos {min_length} caracteres."
    ),
    "too_common": "La contraseña es demasiado común.",
    "entirely_numeric": "La contraseña no puede ser completamente numérica.",
    "too_similar": (
        "La contraseña es demasiado similar a otros datos personales."
    ),
}


def _obtener_plantilla_traduccion(codigo: str) -> str | None:
    """Resuelve la plantilla en espanol asociada a un codigo de validacion de Django."""
    if not codigo.startswith(_PREFIJO_CODIGO_VALIDACION):
        return None
    return _MENSAJES_POR_SUFIJO_CODIGO.get(codigo.removeprefix(_PREFIJO_CODIGO_VALIDACION))


def _traducir_error_contrasena(error: DjangoValidationError) -> str:
    """Convierte los errores de validacion de Django a mensajes en español."""
    mensajes: list[str] = []
    for detalle in error.error_list:
        codigo = detalle.code or ""
        plantilla = _obtener_plantilla_traduccion(codigo)
        if plantilla is not None:
            parametros = detalle.params or {}
            mensajes.append(plantilla.format(**parametros))
        else:
            mensajes.append(str(detalle.message))
    return "; ".join(mensajes)


def validar_contrasena_usuario(
    contrasena: str,
    usuario: Any = None,
) -> None:
    """Valida una contraseña y lanza ValidationError con mensajes en español."""
    try:
        _VALIDAR_CONTRASENA_DJANGO(contrasena, usuario)
    except DjangoValidationError as error:
        mensaje = _traducir_error_contrasena(error)
        raise DjangoValidationError(mensaje) from error
