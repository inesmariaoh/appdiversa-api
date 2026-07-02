"""
Servicios para construir metadatos de interaccion de opciones hacia el frontend.
"""

from typing import Any

from aplicaciones.formularios.constantes_interaccion import (
    AccionInteraccionOpcion,
    ModoCampoTextoOtro,
    ModoExclusionOpciones,
    TipoSeleccionInteraccion,
)
from aplicaciones.formularios.models import TipoPregunta

TIPOS_SELECCION_MULTIPLE = frozenset(
    {
        TipoPregunta.CHECKBOX,
        TipoPregunta.SELECT_MULTIPLE,
    },
)

TIPOS_SELECCION_UNICA = frozenset(
    {
        TipoPregunta.RADIO,
        TipoPregunta.SELECT,
        TipoPregunta.LIKERT,
    },
)


def construir_acciones_ui_opcion(
    activa_otro: bool,
    es_excluyente: bool,
    tipo_pregunta: str,
) -> list[str]:
    """Construye las acciones de interfaz que debe aplicar el frontend."""
    acciones: list[str] = []
    if activa_otro:
        acciones.append(AccionInteraccionOpcion.MOSTRAR_CAMPO_TEXTO)
    if es_excluyente and tipo_pregunta in TIPOS_SELECCION_MULTIPLE:
        acciones.append(AccionInteraccionOpcion.EXCLUIR_OTRAS_OPCIONES)
    return acciones


def _resolver_tipo_seleccion(tipo_pregunta: str) -> str:
    if tipo_pregunta in TIPOS_SELECCION_MULTIPLE:
        return TipoSeleccionInteraccion.MULTIPLE
    if tipo_pregunta in TIPOS_SELECCION_UNICA:
        return TipoSeleccionInteraccion.UNICA
    return TipoSeleccionInteraccion.NO_APLICA


def _resolver_modo_campo_texto_otro(
    permite_otro: bool,
    texto_otro_obligatorio: bool,
    opciones: list[dict[str, Any]],
) -> str:
    if not (permite_otro and any(opcion.get("activa_otro") for opcion in opciones)):
        return ModoCampoTextoOtro.NINGUNO
    if texto_otro_obligatorio:
        return ModoCampoTextoOtro.OBLIGATORIO
    return ModoCampoTextoOtro.OPCIONAL


def construir_comportamiento_interaccion(
    tipo_pregunta: str,
    permite_otro: bool,
    texto_otro_obligatorio: bool,
    opciones: list[dict[str, Any]],
) -> dict[str, str]:
    """Construye las instrucciones de interaccion para una pregunta."""
    comportamiento: dict[str, str] = {
        "tipo_seleccion": _resolver_tipo_seleccion(tipo_pregunta),
        "campo_texto_otro": _resolver_modo_campo_texto_otro(
            permite_otro,
            texto_otro_obligatorio,
            opciones,
        ),
    }
    if (
        tipo_pregunta in TIPOS_SELECCION_MULTIPLE
        and any(opcion.get("es_excluyente") for opcion in opciones)
    ):
        comportamiento["modo_exclusion"] = ModoExclusionOpciones.DESELECCIONAR_OTRAS
    return comportamiento
