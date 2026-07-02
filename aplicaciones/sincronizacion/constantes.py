"""
Constantes y mensajes del motor de sincronizacion offline.
"""


class MensajesSincronizacionApi:
    """Mensajes funcionales de la API de sincronizacion."""

    SESION_NO_EXISTE = "La sesión anónima no existe."
    CHECKSUM_INVALIDO = "El checksum de la operación no es válido."
    OPERACION_DUPLICADA = "La operación ya fue sincronizada."
    RESPUESTA_ELIMINADA = "La respuesta fue eliminada en el servidor."
    PREGUNTA_NO_EXISTE = "La pregunta solicitada no existe para este formulario."
    VALOR_INVALIDO = "El valor enviado no es válido para el tipo de pregunta."
    CONFLICTO_VERSION = "Conflicto de versiones entre cliente y servidor."
    FORMULARIO_FINALIZADO = "La sesión ya fue finalizada."
    OPERACION_ERROR = "No se pudo procesar la operación de sincronización."
    OFFLINE_NO_PERMITIDO = "El formulario no permite la operación sin conexión."
