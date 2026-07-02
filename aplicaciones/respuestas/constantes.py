"""
Mensajes funcionales de la API de respuestas.
"""

class MensajesRespuestaApi:
    """Mensajes de respuesta para endpoints de respuestas."""

    SESION_NO_EXISTE = "La sesión anónima no existe."
    PREGUNTA_NO_EXISTE = "La pregunta solicitada no existe para este formulario."
    VALOR_INVALIDO = "El valor enviado no es válido para el tipo de pregunta."
    VALOR_NO_PERTENECE_CATALOGO = (
        "El valor enviado no pertenece al catálogo asociado a la pregunta."
    )
    ORIGEN_INVALIDO = "El origen de respuesta no es válido."
    FORMULARIO_YA_FINALIZADO = "El formulario ya fue finalizado."
    PREGUNTAS_OBLIGATORIAS_PENDIENTES = (
        "El formulario tiene preguntas obligatorias pendientes."
    )
    FILTROS_NO_CUMPLIDOS = (
        "No se cumplen las condiciones preliminares para diligenciar el formulario."
    )
    FORMULARIO_FINALIZADO_OK = "El formulario fue finalizado correctamente."


class MotivoPreguntaPendiente:
    """Motivos por los que una pregunta queda pendiente de diligenciamiento."""

    OBLIGATORIA_SIN_RESPUESTA = "obligatoria_sin_respuesta"
    TEXTO_OTRO_REQUERIDO = "texto_otro_requerido"


MENSAJES_MOTIVO_PENDIENTE = {
    MotivoPreguntaPendiente.OBLIGATORIA_SIN_RESPUESTA: (
        "Falta responder esta pregunta obligatoria."
    ),
    MotivoPreguntaPendiente.TEXTO_OTRO_REQUERIDO: (
        "Seleccionó la opción \"Otro, ¿cuál?\" y debe especificar el texto."
    ),
}
