"""
Utilidades del motor de formularios para preguntas con catalogos geograficos.
"""

from __future__ import annotations

from aplicaciones.catalogos.constantes import es_tipo_catalogo_geografico
from aplicaciones.formularios.models import Pregunta

TIPOS_PREGUNTA_CATALOGO_GEOGRAFICO = frozenset(
    {
        "select",
        "autocomplete",
    },
)


def es_pregunta_catalogo_geografico(pregunta: Pregunta) -> bool:
    """Indica si la pregunta participa en una jerarquia geografica parametrizable."""
    if not pregunta.usa_catalogo:
        return False

    actual: Pregunta | None = pregunta
    visitados: set[int] = set()
    while actual is not None:
        if actual.pk in visitados:
            return False
        visitados.add(actual.pk)
        if (
            actual.catalogo_asociado is not None
            and es_tipo_catalogo_geografico(actual.catalogo_asociado.tipo_catalogo)
        ):
            return True
        actual = actual.pregunta_padre_catalogo

    return False


def obtener_dependientes_geograficos_ordenados(pregunta: Pregunta) -> list[Pregunta]:
    """Retorna descendientes geograficos activos de una pregunta en orden."""
    if not es_pregunta_catalogo_geografico(pregunta):
        return []

    dependientes: list[Pregunta] = []
    cola = list(
        pregunta.preguntas_dependientes_catalogo.filter(
            esta_activa=True,
            esta_eliminado=False,
        ).order_by("orden"),
    )

    while cola:
        actual = cola.pop(0)
        if not es_pregunta_catalogo_geografico(actual):
            continue
        dependientes.append(actual)
        cola.extend(
            actual.preguntas_dependientes_catalogo.filter(
                esta_activa=True,
                esta_eliminado=False,
            ).order_by("orden"),
        )

    return dependientes
