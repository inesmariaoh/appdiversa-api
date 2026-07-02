"""
Validacion del texto libre obligatorio asociado a opciones tipo otro.
"""

from aplicaciones.formularios.models import Pregunta, TipoPregunta
from aplicaciones.formularios.utilidades_opcion_otro import resolver_activa_otro
from aplicaciones.respuestas.models import Respuesta

TIPOS_SELECCION_MULTIPLE_OTRO = frozenset(
    {
        TipoPregunta.CHECKBOX,
        TipoPregunta.SELECT_MULTIPLE,
    },
)


def _codigos_seleccionados(pregunta: Pregunta, respuesta: Respuesta) -> set[str]:
    """Obtiene los codigos de opcion seleccionados segun el tipo de pregunta."""
    if pregunta.tipo_pregunta in TIPOS_SELECCION_MULTIPLE_OTRO:
        valores = respuesta.valor_json
        if isinstance(valores, list):
            return {str(codigo) for codigo in valores}
        return set()
    texto = respuesta.valor_texto.strip()
    return {texto} if texto else set()


def _hay_opcion_otro_seleccionada(pregunta: Pregunta, codigos: set[str]) -> bool:
    """Indica si alguno de los codigos seleccionados corresponde a una opcion otro."""
    for opcion in pregunta.opciones.all():
        if opcion.codigo not in codigos:
            continue
        if resolver_activa_otro(
            opcion.activa_otro,
            pregunta.permite_otro,
            opcion.etiqueta,
        ):
            return True
    return False


def falta_texto_otro_obligatorio(pregunta: Pregunta, respuesta: Respuesta) -> bool:
    """Evalua si una opcion otro seleccionada carece del texto libre obligatorio."""
    if not (pregunta.permite_otro and pregunta.texto_otro_obligatorio):
        return False
    codigos = _codigos_seleccionados(pregunta, respuesta)
    if not codigos or not _hay_opcion_otro_seleccionada(pregunta, codigos):
        return False
    return not respuesta.observacion.strip()
