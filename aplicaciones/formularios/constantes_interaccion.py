"""
Constantes de comportamiento de interaccion para opciones de preguntas.
"""


class AccionInteraccionOpcion:
    """Acciones que el frontend debe ejecutar al seleccionar una opcion."""

    MOSTRAR_CAMPO_TEXTO = "mostrar_campo_texto"
    EXCLUIR_OTRAS_OPCIONES = "excluir_otras_opciones"


class ModoCampoTextoOtro:
    """Modo del campo de texto libre asociado a opciones otro/cual."""

    OPCIONAL = "opcional"
    OBLIGATORIO = "obligatorio"
    NINGUNO = "ninguno"


class ModoExclusionOpciones:
    """Modo de exclusion en seleccion multiple."""

    DESELECCIONAR_OTRAS = "deseleccionar_otras_al_seleccionar"


class TipoSeleccionInteraccion:
    """Tipo de seleccion que aplica a la pregunta."""

    MULTIPLE = "multiple"
    UNICA = "unica"
    NO_APLICA = "no_aplica"
