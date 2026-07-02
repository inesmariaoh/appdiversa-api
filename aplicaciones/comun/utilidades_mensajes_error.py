"""
Utilidades para normalizar mensajes de error expuestos al cliente.
"""

from aplicaciones.comun.constantes_seguridad import MensajesErrorApi

_SUBCADENAS_VALIDACION_GENERICAS = (
    "este campo es requerido",
    "this field is required",
)

_SUBCADENAS_CSRF = (
    "csrf failed",
    "origin checking failed",
    "csrf token missing",
    "csrf cookie not set",
    "referer checking failed",
)

_SUBCADENAS_TECNICAS = (
    "traceback",
    "exception at",
    "django.db.utils",
    "integrityerror",
    "operationalerror",
)


def _es_mensaje_csrf(texto: str) -> bool:
    """Indica si el mensaje corresponde a un fallo de validacion CSRF."""
    normalizado = texto.lower()
    return any(subcadena in normalizado for subcadena in _SUBCADENAS_CSRF)


def _es_mensaje_tecnico(texto: str) -> bool:
    """Indica si un mensaje contiene detalles tecnicos no aptos para el usuario."""
    normalizado = texto.lower()
    return any(subcadena in normalizado for subcadena in _SUBCADENAS_TECNICAS)


def _es_mensaje_validacion_generica(texto: str) -> bool:
    """Indica si el mensaje corresponde a una validacion generica de campo."""
    normalizado = texto.lower()
    return any(
        subcadena in normalizado for subcadena in _SUBCADENAS_VALIDACION_GENERICAS
    )


def _normalizar_mensaje_lista(mensaje: list[object], defecto: str) -> str:
    """Normaliza un mensaje de error contenido en una lista."""
    if not mensaje:
        return defecto
    return normalizar_mensaje_error_cliente(mensaje[0], defecto)


def _extraer_mensaje_dict(mensaje: dict[object, object]) -> object | None:
    """Extrae el valor relevante de un diccionario de error."""
    if "detalle" in mensaje:
        return mensaje["detalle"]
    if "detail" in mensaje:
        return mensaje["detail"]
    if len(mensaje) == 1:
        return next(iter(mensaje.values()))
    return None


def _normalizar_mensaje_dict(mensaje: dict[object, object], defecto: str) -> str:
    """Normaliza un mensaje de error contenido en un diccionario."""
    valor = _extraer_mensaje_dict(mensaje)
    if valor is None:
        return defecto
    return normalizar_mensaje_error_cliente(valor, defecto)


def _normalizar_mensaje_texto(texto: str, defecto: str) -> str:
    """Normaliza un mensaje de error en formato de texto."""
    if not texto:
        return defecto
    if _es_mensaje_csrf(texto):
        return MensajesErrorApi.SOLICITUD_NO_VALIDA
    if _es_mensaje_validacion_generica(texto):
        return MensajesErrorApi.SOLICITUD_NO_VALIDA
    if _es_mensaje_tecnico(texto):
        return defecto
    return texto


def normalizar_mensaje_error_cliente(
    mensaje: object,
    mensaje_por_defecto: str | None = None,
) -> str:
    """Convierte un mensaje de error interno en texto funcional para el usuario."""
    defecto = mensaje_por_defecto or MensajesErrorApi.ERROR_INESPERADO
    if mensaje is None:
        return defecto
    if isinstance(mensaje, list):
        return _normalizar_mensaje_lista(mensaje, defecto)
    if isinstance(mensaje, dict):
        return _normalizar_mensaje_dict(mensaje, defecto)
    return _normalizar_mensaje_texto(str(mensaje).strip(), defecto)
