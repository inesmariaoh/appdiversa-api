"""
Reordenamiento del flujo visual de preguntas dependientes condicionales.
"""

from aplicaciones.formularios.models import AccionRegla, Pregunta, ReglaPregunta


def construir_mapa_destino_origen_mostrar(
    reglas: list[ReglaPregunta],
) -> dict[str, str]:
    """Construye un mapa codigo_destino -> codigo_origen para reglas de mostrar."""
    mapa: dict[str, str] = {}
    for regla in reglas:
        if regla.accion != AccionRegla.MOSTRAR:
            continue
        if regla.pregunta_destino_id is None:
            continue
        mapa[regla.pregunta_destino.codigo] = regla.pregunta_origen.codigo
    return mapa


def _resolver_codigo_origen_flujo(
    pregunta: Pregunta,
    mapa_destino_origen: dict[str, str],
) -> str | None:
    """Resuelve el codigo de la pregunta origen del flujo visual."""
    if pregunta.pregunta_origen_flujo_id is not None:
        return pregunta.pregunta_origen_flujo.codigo
    return mapa_destino_origen.get(pregunta.codigo)


def ordenar_preguntas_flujo_visual(
    preguntas: list[Pregunta],
    codigos_visibles: frozenset[str],
    mapa_destino_origen: dict[str, str],
) -> list[Pregunta]:
    """Inserta preguntas dependientes inmediatamente despues de su pregunta origen."""
    visibles = [pregunta for pregunta in preguntas if pregunta.codigo in codigos_visibles]
    resultado = list(visibles)

    for dependiente in visibles:
        origen = _resolver_codigo_origen_flujo(dependiente, mapa_destino_origen)
        if origen is None:
            continue
        resultado = [
            pregunta for pregunta in resultado if pregunta.codigo != dependiente.codigo
        ]
        indice_origen = next(
            (indice for indice, pregunta in enumerate(resultado) if pregunta.codigo == origen),
            -1,
        )
        if indice_origen >= 0:
            resultado.insert(indice_origen + 1, dependiente)
        else:
            resultado.append(dependiente)

    return resultado
