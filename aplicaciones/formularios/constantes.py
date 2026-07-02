"""
Mensajes funcionales de la API publica de formularios.
"""


class MensajesFormularioApi:
    """Mensajes de respuesta para endpoints publicos de formularios."""

    FORMULARIO_NO_DISPONIBLE = (
        "El formulario solicitado no se encuentra disponible."
    )
    FORMULARIO_AUN_NO_DISPONIBLE = (
        "El formulario aún no está disponible para ser diligenciado."
    )
    VERSION_NO_DISPONIBLE = (
        "El formulario solicitado no tiene una versión publicada disponible."
    )


class EstadoDisponibilidadFormulario:
    """Estados de disponibilidad publica de un formulario."""

    DISPONIBLE = "disponible"
    PROXIMAMENTE = "proximamente"


class EtiquetaEstadoFormulario:
    """Etiquetas visibles de disponibilidad para el frontend."""

    DISPONIBLE = "Disponible"
    PROXIMAMENTE = "Próximamente"


class FuenteOpciones:
    """Origen de opciones para preguntas de seleccion."""

    CATALOGO = "catalogo"
    OPCIONES = "opciones"
