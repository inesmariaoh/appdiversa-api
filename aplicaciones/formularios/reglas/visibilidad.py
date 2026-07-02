"""
Utilidades de visibilidad y obligatoriedad efectiva segun reglas condicionales.
"""

from aplicaciones.formularios.models import Pregunta
from aplicaciones.formularios.reglas.resultado import ResultadoReglas


def pregunta_visible_efectiva(
    pregunta: Pregunta,
    resultado: ResultadoReglas,
) -> bool:
    """Determina si una pregunta debe mostrarse segun reglas y visibilidad base."""
    codigo = pregunta.codigo
    if codigo in resultado.preguntas_ocultas:
        return False
    if codigo in resultado.preguntas_visibles:
        return True
    return pregunta.visible_por_defecto


def pregunta_obligatoria_efectiva(
    pregunta: Pregunta,
    resultado: ResultadoReglas,
) -> bool:
    """Determina si una pregunta es obligatoria considerando reglas y visibilidad."""
    if not pregunta_visible_efectiva(pregunta, resultado):
        return False

    codigo = pregunta.codigo
    if codigo in resultado.preguntas_obligatorias:
        return True
    if codigo in resultado.preguntas_opcionales:
        return False
    return pregunta.es_obligatoria


def filtrar_preguntas_visibles(
    preguntas: list[Pregunta],
    resultado: ResultadoReglas,
) -> list[Pregunta]:
    """Retorna preguntas visibles segun el resultado del motor de reglas."""
    return [
        pregunta
        for pregunta in preguntas
        if pregunta_visible_efectiva(pregunta, resultado)
    ]
