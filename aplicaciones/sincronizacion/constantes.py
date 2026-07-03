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


class MensajesConflictoApi:
    """Mensajes de la API de resolucion manual de conflictos."""

    SIN_PERMISO = "No tiene permisos para administrar conflictos de sincronización."
    CONFLICTO_NO_ENCONTRADO = "El conflicto de sincronización solicitado no existe."
    RESOLUCION_INVALIDA = "La resolución indicada no es válida."
    VALOR_MANUAL_REQUERIDO = "Debe indicar el valor manual para esta resolución."
    CONFLICTO_SIN_RESPUESTA = (
        "El conflicto no tiene una respuesta asociada para aplicar el valor."
    )
    CONFLICTO_RESUELTO = "El conflicto se resolvió correctamente."


class FiltrosConflicto:
    """Nombres de los parametros de filtrado de conflictos."""

    TIPO_CONFLICTO = "tipo_conflicto"
    RESOLUCION = "resolucion"
    RESUELTO = "resuelto"
    UUID_LOCAL = "uuid_local"
