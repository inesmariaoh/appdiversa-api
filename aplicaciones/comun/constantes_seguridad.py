"""
Constantes de seguridad transversal de la API.
"""

HEADER_API_INTERNA = "HTTP_X_API_INTERNA"
HEADER_TOKEN_SESION = "HTTP_X_TOKEN_SESION"


class MensajesAccesoApi:
    """Mensajes funcionales de acceso a la API."""

    API_INTERNA_NO_CONFIGURADA = (
        "El acceso interno de la API no está disponible en este entorno."
    )
    API_INTERNA_INVALIDA = "El acceso interno de la API no está autorizado."
    ACCESO_DENEGADO = "No tiene permiso para realizar esta operación."


class MensajesErrorApi:
    """Mensajes funcionales genéricos para errores de la API."""

    SOLICITUD_NO_VALIDA = (
        "No fue posible procesar la solicitud. Recargue la página e intente nuevamente."
    )
    ERROR_INESPERADO = (
        "Ocurrió un error inesperado. Intente nuevamente más tarde."
    )
