"""
Utilidades para detectar opciones excluyentes o de negacion en seleccion multiple.
"""

import re
import unicodedata

from aplicaciones.formularios.models import TipoPregunta

TIPOS_PREGUNTA_OPCION_EXCLUYENTE = frozenset(
    {
        TipoPregunta.CHECKBOX,
        TipoPregunta.SELECT_MULTIPLE,
    },
)

_PATRON_ETIQUETA_OPCION_EXCLUYENTE = re.compile(
    r"(?i)^("
    r"no he\b|"
    r"nunca\b|"
    r"no me ha\b|"
    r"no me han\b|"
    r"ningun\b|"
    r"ninguna\b|"
    r"no aplica\b"
    r")",
)


def _normalizar_etiqueta(etiqueta: str) -> str:
    """Normaliza la etiqueta eliminando acentos para comparaciones consistentes."""
    texto = unicodedata.normalize("NFD", etiqueta.strip().lower())
    return "".join(caracter for caracter in texto if unicodedata.category(caracter) != "Mn")


def etiqueta_es_opcion_excluyente(etiqueta: str) -> bool:
    """Indica si la etiqueta sugiere una respuesta de negacion o no aplica."""
    if not etiqueta.strip():
        return False
    return (
        _PATRON_ETIQUETA_OPCION_EXCLUYENTE.search(_normalizar_etiqueta(etiqueta))
        is not None
    )


def resolver_es_excluyente(
    opcion_es_excluyente: bool,
    tipo_pregunta: str,
    etiqueta: str,
) -> bool:
    """Resuelve si una opcion debe comportarse como excluyente en la interfaz."""
    if tipo_pregunta not in TIPOS_PREGUNTA_OPCION_EXCLUYENTE:
        return False
    if opcion_es_excluyente:
        return True
    return etiqueta_es_opcion_excluyente(etiqueta)
