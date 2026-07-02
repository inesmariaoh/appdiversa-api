"""
Mensajes funcionales de la API administrativa de formularios.
"""


class MensajesFormularioAdmin:
    """Mensajes de respuesta para operaciones administrativas."""

    FORMULARIO_NO_ENCONTRADO = "El formulario solicitado no existe."
    VERSION_NO_ENCONTRADA = "La versión solicitada no existe."
    SECCION_NO_ENCONTRADA = "La sección solicitada no existe."
    PREGUNTA_NO_ENCONTRADA = "La pregunta solicitada no existe."
    OPCION_NO_ENCONTRADA = "La opción solicitada no existe."
    REGLA_NO_ENCONTRADA = "La regla solicitada no existe."
    TEXTO_NO_ENCONTRADO = "El texto solicitado no existe."
    CODIGO_DUPLICADO = "Ya existe un registro activo con el código indicado."
    SIN_VERSION_PARA_PUBLICAR = (
        "No se puede publicar un formulario sin al menos una versión."
    )
    VERSION_SIN_SECCIONES = (
        "No se puede publicar una versión sin secciones activas."
    )
    SECCION_SIN_PREGUNTAS = (
        "No se puede publicar una versión con secciones activas sin preguntas."
    )
    VERSION_PUBLICADA_CON_RESPUESTAS = (
        "No se puede editar una versión publicada que ya tiene respuestas."
    )
    VERSION_NO_EDITABLE = "La versión indicada no permite edición."
    REGLA_DESTINO_INVALIDA = (
        "La regla requiere pregunta destino o sección destino según la acción."
    )
    CATALOGO_INCONSISTENTE = (
        "La pregunta con catálogo asociado debe tener usa_catalogo activo."
    )
    TOOLTIP_TEXTO_OBLIGATORIO = (
        "El texto del tooltip es obligatorio cuando está activado."
    )
    PUBLICACION_NO_AUTORIZADA = (
        "No tiene permisos para publicar o versionar formularios."
    )
